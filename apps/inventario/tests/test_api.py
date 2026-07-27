"""Pruebas de integracion de la API de inventario."""

import pytest
from rest_framework.test import APIClient

from apps.inventario.infrastructure.models import MovimientoInventarioModel

pytestmark = pytest.mark.django_db

URL_INGRESOS = "/api/stock/ingresos/"
URL_SALIDAS = "/api/stock/salidas/"
URL_STOCK = "/api/stock/"
VARIANTE_INEXISTENTE = "00000000-0000-4000-8000-000000000000"


def test_anonimo_no_puede_registrar_movimientos(variante_id) -> None:
    """El endpoint quedo cerrado: sin sesion no se toca el inventario."""
    respuesta = APIClient().post(
        URL_INGRESOS,
        {"variante_id": variante_id, "cantidad": 1, "motivo": "Ingreso"},
        format="json",
    )

    assert respuesta.status_code in {401, 403}
    assert MovimientoInventarioModel.objects.count() == 0


def test_ingreso_api_incrementa_stock_y_crea_un_movimiento(
    client,
    stock,
    variante_id,
) -> None:
    respuesta = client.post(
        URL_INGRESOS,
        {"variante_id": variante_id, "cantidad": 5, "motivo": "Ingreso API"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert respuesta.data["tipo"] == "ingreso"
    assert respuesta.data["cantidad"] == 5
    assert stock.cantidad_actual == 15
    assert MovimientoInventarioModel.objects.count() == 1


@pytest.mark.usefixtures("stock")
def test_el_responsable_sale_de_la_sesion_y_no_del_cuerpo(
    client,
    variante_id,
    usuario_autenticado,
) -> None:
    """Mandar `usuario_id` en el cuerpo no permite suplantar a nadie."""
    respuesta = client.post(
        URL_INGRESOS,
        {
            "variante_id": variante_id,
            "cantidad": 1,
            "motivo": "Ingreso API",
            "usuario_id": VARIANTE_INEXISTENTE,
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["registrado_por"] == usuario_autenticado.id


def test_segundo_ingreso_api_acumula_stock(client, stock, variante_id) -> None:
    client.post(
        URL_INGRESOS,
        {"variante_id": variante_id, "cantidad": 5, "motivo": "Ingreso 1"},
        format="json",
    )
    respuesta = client.post(
        URL_INGRESOS,
        {"variante_id": variante_id, "cantidad": 2, "motivo": "Ingreso 2"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert stock.cantidad_actual == 17
    assert MovimientoInventarioModel.objects.count() == 2


@pytest.mark.parametrize("cantidad", [0, -1, "abc"])
def test_ingreso_con_cantidad_invalida_lo_rechaza_el_serializer(
    client,
    stock,
    variante_id,
    cantidad,
) -> None:
    respuesta = client.post(
        URL_INGRESOS,
        {"variante_id": variante_id, "cantidad": cantidad, "motivo": "Ingreso"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert "cantidad" in respuesta.data
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


def test_ingreso_con_stock_inexistente_devuelve_404(
    client,
    crear_variante,
) -> None:
    """La variante existe en el catalogo, pero nunca se le dio de alta stock."""
    variante_sin_stock = crear_variante(talla="XL")

    respuesta = client.post(
        URL_INGRESOS,
        {
            "variante_id": str(variante_sin_stock.id),
            "cantidad": 1,
            "motivo": "Ingreso",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "No existe stock para la variante"


def test_crear_stock_con_variante_inexistente_devuelve_404(client) -> None:
    respuesta = client.post(
        URL_STOCK,
        {
            "variante_id": VARIANTE_INEXISTENTE,
            "stock_inicial": 5,
            "stock_minimo": 1,
            "ubicacion": "almacen",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "La variante no existe"


def test_crear_stock_duplicado_devuelve_409(client, stock, variante_id) -> None:
    respuesta = client.post(
        URL_STOCK,
        {
            "variante_id": variante_id,
            "stock_inicial": 5,
            "stock_minimo": 1,
            "ubicacion": "almacen",
        },
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 409
    assert respuesta.data["error"] == "Ya existe stock para la variante"
    assert stock.cantidad_actual == 10


def test_salida_api_descuenta_stock_y_crea_un_movimiento(
    client,
    stock,
    variante_id,
) -> None:
    respuesta = client.post(
        URL_SALIDAS,
        {"variante_id": variante_id, "cantidad": 4, "motivo": "Salida API"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert respuesta.data["tipo"] == "salida"
    assert respuesta.data["cantidad"] == 4
    assert stock.cantidad_actual == 6
    assert MovimientoInventarioModel.objects.count() == 1


def test_salida_exacta_deja_stock_en_cero(client, stock, variante_id) -> None:
    respuesta = client.post(
        URL_SALIDAS,
        {"variante_id": variante_id, "cantidad": 10, "motivo": "Salida total"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert stock.cantidad_actual == 0
    assert MovimientoInventarioModel.objects.count() == 1


def test_salida_con_stock_insuficiente_no_cambia_el_stock(
    client,
    stock,
    variante_id,
) -> None:
    respuesta = client.post(
        URL_SALIDAS,
        {"variante_id": variante_id, "cantidad": 11, "motivo": "Salida"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert respuesta.data["error"] == "No hay stock suficiente para la salida"
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


def test_salida_no_dispone_del_stock_reservado(
    client,
    stock,
    variante_id,
    servicio_inventario,
) -> None:
    """Lo reservado para un pedido no puede salir por otra via."""
    servicio_inventario.reservar(variante_id, 8)

    respuesta = client.post(
        URL_SALIDAS,
        {"variante_id": variante_id, "cantidad": 5, "motivo": "Salida"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert stock.cantidad_actual == 10
