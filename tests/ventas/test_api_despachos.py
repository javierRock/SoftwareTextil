"""Seguridad e invariantes de la API de despachos."""

from decimal import Decimal
from types import SimpleNamespace

import pytest
from rest_framework.test import APIClient

from apps.inventario.models import MovimientoInventarioModel, StockVarianteModel
from apps.ventas.models import DespachoModel, DetallePedidoModel, PedidoModel

pytestmark = pytest.mark.django_db
URL = "/api/ventas/despachos/"


def api_para(modelo, rol: str) -> APIClient:
    api = APIClient()
    api.force_authenticate(
        user=SimpleNamespace(
            id=str(modelo.id),
            rol=rol,
            is_authenticated=True,
        )
    )
    return api


@pytest.fixture
def encargado(crear_usuario):
    return crear_usuario(nombre="Encargado", rol="Encargado de inventario")


@pytest.fixture
def pedido_pagado(crear_usuario, crear_carrito):
    cliente = crear_usuario(nombre="Cliente despacho")
    return PedidoModel.objects.create(
        cliente=cliente,
        carrito=crear_carrito(cliente),
        total_monto=Decimal("50.00"),
        estado="pagado",
    )


def test_despachos_requieren_rol_autorizado(
    crear_usuario, pedido_pagado
) -> None:
    cliente = crear_usuario(nombre="Cliente sin permiso")
    cuerpo = {
        "pedido_id": str(pedido_pagado.id),
        "direccion_entrega": "Av. Textil 123",
    }

    assert APIClient().get(URL).status_code == 401
    respuesta = api_para(cliente, "Cliente").post(URL, cuerpo, format="json")
    assert respuesta.status_code == 403


def test_encargado_puede_listar_pedidos_pagados(encargado, pedido_pagado) -> None:
    respuesta = api_para(encargado, "Encargado de inventario").get(
        "/api/ventas/pedidos/"
    )

    assert respuesta.status_code == 200
    assert [pedido["id"] for pedido in respuesta.data] == [str(pedido_pagado.id)]


def test_solo_programa_pedidos_pagados(encargado, crear_pedido) -> None:
    pedido = crear_pedido()

    respuesta = api_para(encargado, "Encargado de inventario").post(
        URL,
        {"pedido_id": str(pedido.id), "direccion_entrega": "Av. Textil 123"},
        format="json",
    )

    assert respuesta.status_code == 400
    assert DespachoModel.objects.count() == 0


def test_responsable_derivado_y_confirmacion_crea_guia_atomicamente(
    encargado, pedido_pagado
) -> None:
    api = api_para(encargado, "Encargado de inventario")
    creado = api.post(
        URL,
        {
            "pedido_id": str(pedido_pagado.id),
            "direccion_entrega": "Av. Textil 123",
        },
        format="json",
    )
    despacho_id = creado.data["id"]

    preparado = api.post(
        f"{URL}{despacho_id}/preparar/",
        {"responsable_id": "00000000-0000-0000-0000-000000000000"},
        format="json",
    )
    confirmado = api.post(
        f"{URL}{despacho_id}/confirmar/",
        {"serie": "T001", "numero": "42", "transportista": "Textil Express"},
        format="json",
    )

    assert preparado.status_code == 200
    assert preparado.data["responsable_id"] == str(encargado.id)
    assert confirmado.status_code == 200
    assert confirmado.data["estado"] == "confirmado"
    assert confirmado.data["guia"]["numero"] == "42"


def test_despacho_cancelado_no_puede_reabrirse(encargado, pedido_pagado) -> None:
    api = api_para(encargado, "Encargado de inventario")
    despacho_id = api.post(
        URL,
        {
            "pedido_id": str(pedido_pagado.id),
            "direccion_entrega": "Av. Textil 123",
        },
        format="json",
    ).data["id"]
    api.post(f"{URL}{despacho_id}/cancelar/")

    respuesta = api.post(f"{URL}{despacho_id}/preparar/", {}, format="json")

    assert respuesta.status_code == 409
    assert DespachoModel.objects.get(id=despacho_id).estado == "cancelado"


def test_despacho_confirmado_no_puede_cancelarse(encargado, pedido_pagado) -> None:
    api = api_para(encargado, "Encargado de inventario")
    despacho_id = api.post(
        URL,
        {
            "pedido_id": str(pedido_pagado.id),
            "direccion_entrega": "Av. Textil 123",
        },
        format="json",
    ).data["id"]
    api.post(f"{URL}{despacho_id}/preparar/", {})
    api.post(
        f"{URL}{despacho_id}/confirmar/",
        {"serie": "T001", "numero": "43"},
        format="json",
    )

    respuesta = api.post(f"{URL}{despacho_id}/cancelar/")

    assert respuesta.status_code == 409


def test_confirmar_despacho_consume_reserva_y_registra_salida(
    encargado,
    pedido_pagado,
    crear_variante,
) -> None:
    variante = crear_variante()
    stock = StockVarianteModel.objects.create(
        variante=variante,
        cantidad_actual=10,
        cantidad_reservada=2,
        nivel_minimo=1,
    )
    DetallePedidoModel.objects.create(
        pedido=pedido_pagado,
        variante=variante,
        cantidad=2,
        precio_monto=Decimal("25.00"),
    )
    api = api_para(encargado, "Encargado de inventario")
    despacho_id = api.post(
        URL,
        {
            "pedido_id": str(pedido_pagado.id),
            "direccion_entrega": "Av. Textil 123",
        },
        format="json",
    ).data["id"]
    api.post(f"{URL}{despacho_id}/preparar/", {})

    respuesta = api.post(
        f"{URL}{despacho_id}/confirmar/",
        {"serie": "T002", "numero": "1"},
        format="json",
    )

    stock.refresh_from_db()
    assert respuesta.status_code == 200
    assert stock.cantidad_actual == 8
    assert stock.cantidad_reservada == 0
    movimiento = MovimientoInventarioModel.objects.get(stock=stock)
    assert movimiento.tipo == "salida"
    assert movimiento.cantidad == 2
    assert movimiento.registrado_por_id == encargado.id
