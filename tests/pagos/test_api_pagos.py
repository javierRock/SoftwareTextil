"""Pruebas de integracion y seguridad de la API REST de pagos."""

from decimal import Decimal
from types import SimpleNamespace
from typing import Any

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.models import PagoModel, PedidoModel
from apps.ventas.pagos.domain.excepciones import PedidoNoAdmitePago
from apps.ventas.pagos.infrastructure.pedidos import DjangoRepositorioPedidoPago

pytestmark = pytest.mark.django_db
URL_PAGOS = "/api/ventas/pagos/"


@pytest.fixture
def cliente() -> SimpleNamespace:
    return SimpleNamespace(id="cliente-1", rol="Cliente", is_authenticated=True)


@pytest.fixture
def otro_cliente() -> SimpleNamespace:
    return SimpleNamespace(id="cliente-2", rol="Cliente", is_authenticated=True)


@pytest.fixture
def administrador() -> SimpleNamespace:
    return SimpleNamespace(id="admin-1", rol="Administrador", is_authenticated=True)


@pytest.fixture
def pedido(cliente: SimpleNamespace) -> PedidoModel:
    return PedidoModel.objects.create(
        cliente_id=cliente.id,
        carrito_id="carrito-1",
        total_monto=Decimal("120.50"),
        total_moneda="PEN",
    )


def api_autenticada(usuario: SimpleNamespace) -> APIClient:
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


def datos_pago(pedido_id: str, **cambios: Any) -> dict[str, str]:
    datos = {
        "pedido_id": pedido_id,
        "monto": "120.50",
        "metodo": "tarjeta",
        "referencia": "operacion-456",
    }
    datos.update(cambios)
    return datos


def registrar_pago(
    api: APIClient,
    pedido: PedidoModel,
    **cambios: Any,
) -> Response:
    return api.post(URL_PAGOS, datos_pago(str(pedido.id), **cambios), format="json")


def test_anonimo_no_puede_operar_pagos() -> None:
    api = APIClient()

    assert api.get(URL_PAGOS).status_code == 401
    assert api.post(URL_PAGOS, {}, format="json").status_code == 401


def test_cliente_registra_pago_total_propio(
    cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    respuesta = registrar_pago(api_autenticada(cliente), pedido)

    assert respuesta.status_code == 201
    assert respuesta.data["estado"] == "pendiente"
    assert respuesta.data["monto_monto"] == "120.50"


def test_cliente_no_paga_pedido_ajeno(
    otro_cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    respuesta = registrar_pago(api_autenticada(otro_cliente), pedido)

    assert respuesta.status_code == 403
    assert respuesta.data["codigo"] == "pedido_no_pertenece_cliente"


def test_rechaza_monto_distinto_al_total(
    cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    respuesta = registrar_pago(api_autenticada(cliente), pedido, monto="100.00")

    assert respuesta.status_code == 400
    assert respuesta.data["codigo"] == "monto_no_coincide_con_pedido"


def test_rechaza_metodo_y_campos_desconocidos(
    cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    api = api_autenticada(cliente)

    metodo = registrar_pago(api, pedido, metodo="bitcoin")
    sensible = registrar_pago(api, pedido, cvv="123")

    assert metodo.status_code == 400
    assert metodo.data["codigo"] == "entrada_invalida"
    assert sensible.status_code == 400
    assert sensible.data["codigo"] == "entrada_invalida"


def test_impide_pago_duplicado(
    cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    api = api_autenticada(cliente)
    registrar_pago(api, pedido)

    respuesta = registrar_pago(api, pedido)

    assert respuesta.status_code == 409
    assert respuesta.data["codigo"] == "pago_pedido_duplicado"


def test_cliente_no_puede_aprobar(
    cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    api = api_autenticada(cliente)
    pago_id = registrar_pago(api, pedido).data["id"]

    respuesta = api.post(f"{URL_PAGOS}{pago_id}/aprobar/")

    assert respuesta.status_code == 403


def test_administrador_aprueba_y_marca_pedido_pagado(
    cliente: SimpleNamespace,
    administrador: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    pago_id = registrar_pago(api_autenticada(cliente), pedido).data["id"]

    respuesta = api_autenticada(administrador).post(f"{URL_PAGOS}{pago_id}/aprobar/")

    assert respuesta.status_code == 200
    assert respuesta.data["estado"] == "aprobado"
    pedido.refresh_from_db()
    assert pedido.estado == EstadoPedido.PAGADO.value


def test_aprobacion_revierte_pago_si_falla_actualizacion_del_pedido(
    cliente: SimpleNamespace,
    administrador: SimpleNamespace,
    pedido: PedidoModel,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pago_id = registrar_pago(api_autenticada(cliente), pedido).data["id"]

    def fallar_actualizacion(
        _repositorio: DjangoRepositorioPedidoPago,
        _pedido_id: str,
    ) -> None:
        raise PedidoNoAdmitePago()

    monkeypatch.setattr(
        DjangoRepositorioPedidoPago,
        "marcar_pagado",
        fallar_actualizacion,
    )

    respuesta = api_autenticada(administrador).post(f"{URL_PAGOS}{pago_id}/aprobar/")

    assert respuesta.status_code == 409
    assert PagoModel.objects.get(id=pago_id).estado == "pendiente"
    pedido.refresh_from_db()
    assert pedido.estado == EstadoPedido.CREADO.value


def test_transicion_repetida_devuelve_409(
    cliente: SimpleNamespace,
    administrador: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    pago_id = registrar_pago(api_autenticada(cliente), pedido).data["id"]
    api = api_autenticada(administrador)
    url = f"{URL_PAGOS}{pago_id}/rechazar/"
    api.post(url)

    respuesta = api.post(url)

    assert respuesta.status_code == 409
    assert respuesta.data["codigo"] == "pago_ya_procesado"


def test_cliente_lista_solo_sus_pagos_paginados(
    cliente: SimpleNamespace,
    otro_cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    otro_pedido = PedidoModel.objects.create(
        cliente_id=otro_cliente.id,
        carrito_id="carrito-2",
        total_monto=Decimal("120.50"),
    )
    esperado = registrar_pago(api_autenticada(cliente), pedido).data["id"]
    registrar_pago(api_autenticada(otro_cliente), otro_pedido)

    respuesta = api_autenticada(cliente).get(URL_PAGOS, {"pagina": 1, "tamano": 1})

    assert respuesta.status_code == 200
    assert respuesta.data["total"] == 1
    assert [pago["id"] for pago in respuesta.data["resultados"]] == [esperado]


def test_cliente_no_consulta_detalle_ajeno(
    cliente: SimpleNamespace,
    otro_cliente: SimpleNamespace,
    pedido: PedidoModel,
) -> None:
    pago_id = registrar_pago(api_autenticada(cliente), pedido).data["id"]

    respuesta = api_autenticada(otro_cliente).get(f"{URL_PAGOS}{pago_id}/")

    assert respuesta.status_code == 403
