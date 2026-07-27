"""Pruebas de integracion del API de carrito y pedidos.

Recorren el flujo completo (HTTP -> vista -> caso de uso -> repositorio Django)
para verificar que la refactorizacion SOLID no altero el contrato publico:
mismos endpoints, mismos campos y mismos codigos de estado.
"""

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def cliente_id(crear_usuario) -> str:
    """Las FK exigen un cliente real, no un identificador inventado."""
    return str(crear_usuario().id)


@pytest.fixture
def variante_id(crear_variante) -> str:
    return str(crear_variante().id)


@pytest.fixture
def carrito_con_items(api, cliente_id, variante_id):
    respuesta = api.post(
        "/api/ventas/carritos/", {"cliente_id": cliente_id}, format="json"
    )
    carrito_id = respuesta.data["id"]
    api.post(
        f"/api/ventas/carritos/{carrito_id}/items/",
        {"variante_id": variante_id, "cantidad": 2, "precio_monto": "30.00"},
        format="json",
    )
    return carrito_id


@pytest.mark.django_db
def test_crear_carrito_devuelve_el_agregado(api, cliente_id):
    respuesta = api.post(
        "/api/ventas/carritos/", {"cliente_id": cliente_id}, format="json"
    )

    assert respuesta.status_code == 201
    assert respuesta.data["cliente_id"] == cliente_id
    assert respuesta.data["estado"] == "abierto"
    assert respuesta.data["items"] == []


@pytest.mark.django_db
def test_agregar_y_quitar_items(api, carrito_con_items, variante_id):
    detalle = api.get(f"/api/ventas/carritos/{carrito_con_items}/")
    assert detalle.status_code == 200
    assert len(detalle.data["items"]) == 1
    assert detalle.data["items"][0]["precio_monto"] == "30.00"

    quitado = api.delete(
        f"/api/ventas/carritos/{carrito_con_items}/items/",
        {"variante_id": variante_id},
        format="json",
    )
    assert quitado.status_code == 200
    assert quitado.data["items"] == []


@pytest.mark.django_db
def test_carrito_inexistente_responde_404(api):
    respuesta = api.get("/api/ventas/carritos/carrito-fantasma/")

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "Carrito no encontrado"


@pytest.mark.django_db
def test_generar_pedido_y_cancelarlo(api, carrito_con_items, cliente_id):
    creado = api.post(
        "/api/ventas/pedidos/",
        {"carrito_id": carrito_con_items, "cliente_id": cliente_id},
        format="json",
    )
    assert creado.status_code == 201
    assert creado.data["total_monto"] == "60.00"
    assert creado.data["estado"] == "creado"
    assert len(creado.data["detalles"]) == 1

    pedido_id = creado.data["id"]
    listado = api.get("/api/ventas/pedidos/", {"cliente_id": cliente_id})
    assert [p["id"] for p in listado.data] == [pedido_id]

    cancelado = api.post(f"/api/ventas/pedidos/{pedido_id}/cancelar/", format="json")
    assert cancelado.status_code == 200
    assert cancelado.data["estado"] == "cancelado"


@pytest.mark.django_db
def test_no_se_generan_dos_pedidos_del_mismo_carrito(
    api,
    carrito_con_items,
    cliente_id,
):
    cuerpo = {"carrito_id": carrito_con_items, "cliente_id": cliente_id}
    api.post("/api/ventas/pedidos/", cuerpo, format="json")

    repetido = api.post("/api/ventas/pedidos/", cuerpo, format="json")

    assert repetido.status_code == 400
    assert repetido.data["error"] == "El carrito no esta abierto"


@pytest.mark.django_db
def test_pedido_inexistente_responde_404(api):
    respuesta = api.get("/api/ventas/pedidos/pedido-fantasma/")

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "Pedido no encontrado"
