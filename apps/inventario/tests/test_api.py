"""Pruebas de integracion de la API de inventario."""

import pytest

from apps.catalogo.infrastructure.models import PrendaModel
from apps.inventario.infrastructure.models import MovimientoInventarioModel


@pytest.mark.django_db
def test_ingreso_api_incrementa_stock_y_crea_un_movimiento(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-1", "cantidad": 5, "motivo": "Ingreso API", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert respuesta.data["tipo"] == "ingreso"
    assert respuesta.data["cantidad"] == 5
    assert stock.cantidad_actual == 15
    assert MovimientoInventarioModel.objects.count() == 1


@pytest.mark.django_db
def test_ingreso_prioriza_request_user_sobre_usuario_id_del_cliente(client, stock, prenda, usuario_autenticado) -> None:
    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-1", "cantidad": 1, "motivo": "Ingreso API", "usuario_id": "usuario-falso"},
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["registrado_por"] == str(usuario_autenticado.id)


@pytest.mark.django_db
def test_segundo_ingreso_api_acumula_stock(client, stock, prenda) -> None:
    client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-1", "cantidad": 5, "motivo": "Ingreso 1", "usuario_id": "usuario-1"},
        format="json",
    )
    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-1", "cantidad": 2, "motivo": "Ingreso 2", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert stock.cantidad_actual == 17
    assert MovimientoInventarioModel.objects.count() == 2


@pytest.mark.django_db
def test_ingreso_con_cantidad_cero_es_rechazado_por_serializer(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-1", "cantidad": 0, "motivo": "Ingreso", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert "cantidad" in respuesta.data
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_ingreso_con_cantidad_negativa_es_rechazado_por_serializer(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-1", "cantidad": -1, "motivo": "Ingreso", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert "cantidad" in respuesta.data
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_ingreso_con_cantidad_no_numerica_es_rechazado_por_serializer(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-1", "cantidad": "abc", "motivo": "Ingreso", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert "cantidad" in respuesta.data
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_ingreso_con_prenda_inexistente_devuelve_404(client) -> None:
    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-inexistente", "cantidad": 1, "motivo": "Ingreso", "usuario_id": "usuario-1"},
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "La prenda no existe"


@pytest.mark.django_db
def test_ingreso_con_stock_inexistente_devuelve_404(client, categoria) -> None:
    PrendaModel.objects.create(
        id="prenda-2",
        nombre="Polo 2",
        descripcion="Sin stock",
        precio_monto="20.00",
        precio_moneda="PEN",
        categoria=categoria,
        estado="activa",
        registrado_por="usuario-1",
    )

    respuesta = client.post(
        "/api/stock/ingresos/",
        {"prenda_id": "prenda-2", "cantidad": 1, "motivo": "Ingreso", "usuario_id": "usuario-1"},
        format="json",
    )

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "No existe stock para la prenda"


@pytest.mark.django_db
def test_salida_api_descuenta_stock_y_crea_un_movimiento(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/salidas/",
        {"prenda_id": "prenda-1", "cantidad": 4, "motivo": "Salida API", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert respuesta.data["tipo"] == "salida"
    assert respuesta.data["cantidad"] == 4
    assert stock.cantidad_actual == 6
    assert MovimientoInventarioModel.objects.count() == 1


@pytest.mark.django_db
def test_salida_exacta_deja_stock_en_cero(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/salidas/",
        {"prenda_id": "prenda-1", "cantidad": 10, "motivo": "Salida total", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 201
    assert stock.cantidad_actual == 0
    assert MovimientoInventarioModel.objects.count() == 1


@pytest.mark.django_db
def test_salida_con_stock_insuficiente_es_rechazada_sin_cambiar_stock(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/salidas/",
        {"prenda_id": "prenda-1", "cantidad": 11, "motivo": "Salida", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert respuesta.data["error"] == "No hay stock suficiente para la salida"
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_salida_con_cantidad_no_numerica_es_rechazada_por_serializer(client, stock, prenda) -> None:
    respuesta = client.post(
        "/api/stock/salidas/",
        {"prenda_id": "prenda-1", "cantidad": "abc", "motivo": "Salida", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()

    assert respuesta.status_code == 400
    assert "cantidad" in respuesta.data
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0
