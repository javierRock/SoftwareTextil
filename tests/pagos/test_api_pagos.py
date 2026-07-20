"""Pruebas de integracion de la API REST de pagos."""

from typing import Any

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient


pytestmark = pytest.mark.django_db

URL_PAGOS = "/api/ventas/pagos/"


@pytest.fixture
def cliente_api() -> APIClient:
    return APIClient()


def datos_pago(
    pedido_id: str = "pedido-1",
    metodo: str = "tarjeta",
) -> dict[str, str]:
    return {
        "pedido_id": pedido_id,
        "monto": "120.50",
        "metodo": metodo,
        "referencia": "operacion-456",
    }


def registrar_pago(cliente_api: APIClient, **cambios: Any) -> Response:
    datos = datos_pago()
    datos.update(cambios)
    return cliente_api.post(URL_PAGOS, datos, format="json")


def test_post_valido_devuelve_201(cliente_api: APIClient) -> None:
    respuesta = registrar_pago(cliente_api)

    assert respuesta.status_code == 201
    assert respuesta.data["estado"] == "pendiente"
    assert respuesta.data["monto_monto"] == "120.50"


@pytest.mark.parametrize(
    ("cambios", "codigo"),
    [
        ({"monto": "0.00"}, "monto_pago_invalido"),
        ({"monto": "-1.00"}, "monto_pago_invalido"),
        ({"metodo": "bitcoin"}, "metodo_pago_no_soportado"),
        ({"referencia": ""}, "referencia_pago_invalida"),
    ],
)
def test_post_invalido_devuelve_400(
    cliente_api: APIClient,
    cambios: dict[str, str],
    codigo: str,
) -> None:
    respuesta = registrar_pago(cliente_api, **cambios)

    assert respuesta.status_code == 400
    assert respuesta.data["codigo"] == codigo


def test_no_acepta_datos_sensibles_de_tarjeta(cliente_api: APIClient) -> None:
    respuesta = registrar_pago(
        cliente_api,
        numero_tarjeta="4111111111111111",
        cvv="123",
    )

    assert respuesta.status_code == 400
    assert respuesta.data["codigo"] == "entrada_invalida"


def test_get_por_id_devuelve_200(cliente_api: APIClient) -> None:
    pago_id = registrar_pago(cliente_api).data["id"]

    respuesta = cliente_api.get(f"{URL_PAGOS}{pago_id}/")

    assert respuesta.status_code == 200
    assert respuesta.data["id"] == pago_id


def test_get_inexistente_devuelve_404(cliente_api: APIClient) -> None:
    respuesta = cliente_api.get(f"{URL_PAGOS}pago-inexistente/")

    assert respuesta.status_code == 404
    assert respuesta.data["codigo"] == "pago_no_encontrado"


def test_listar_todos_los_pagos(cliente_api: APIClient) -> None:
    registrar_pago(cliente_api, pedido_id="pedido-1")
    registrar_pago(cliente_api, pedido_id="pedido-2")

    respuesta = cliente_api.get(URL_PAGOS)

    assert respuesta.status_code == 200
    assert len(respuesta.data) == 2


def test_filtrar_por_pedido(cliente_api: APIClient) -> None:
    esperado = registrar_pago(cliente_api, pedido_id="pedido-1").data["id"]
    registrar_pago(cliente_api, pedido_id="pedido-2")

    respuesta = cliente_api.get(URL_PAGOS, {"pedido_id": "pedido-1"})

    assert respuesta.status_code == 200
    assert [pago["id"] for pago in respuesta.data] == [esperado]


def test_aprobar_devuelve_200(cliente_api: APIClient) -> None:
    pago_id = registrar_pago(cliente_api).data["id"]

    respuesta = cliente_api.post(f"{URL_PAGOS}{pago_id}/aprobar/")

    assert respuesta.status_code == 200
    assert respuesta.data["estado"] == "aprobado"


def test_rechazar_devuelve_200(cliente_api: APIClient) -> None:
    pago_id = registrar_pago(cliente_api).data["id"]

    respuesta = cliente_api.post(f"{URL_PAGOS}{pago_id}/rechazar/")

    assert respuesta.status_code == 200
    assert respuesta.data["estado"] == "rechazado"


@pytest.mark.parametrize("transicion", ["aprobar", "rechazar"])
def test_transicion_repetida_devuelve_409(
    cliente_api: APIClient,
    transicion: str,
) -> None:
    pago_id = registrar_pago(cliente_api).data["id"]
    url = f"{URL_PAGOS}{pago_id}/{transicion}/"
    cliente_api.post(url)

    respuesta = cliente_api.post(url)

    assert respuesta.status_code == 409
    assert respuesta.data["codigo"] == "pago_ya_procesado"
