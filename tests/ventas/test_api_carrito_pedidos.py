"""Integracion y seguridad del API de carrito y pedidos."""

from decimal import Decimal
from types import SimpleNamespace

import pytest
from rest_framework.test import APIClient

from apps.inventario.models import StockVarianteModel
from apps.ventas.models import CarritoModel, PedidoModel

pytestmark = pytest.mark.django_db


def usuario_api(modelo, rol: str = "Cliente") -> SimpleNamespace:
    return SimpleNamespace(
        id=str(modelo.id),
        rol=rol,
        is_authenticated=True,
    )


def api_autenticada(usuario) -> APIClient:
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def cliente(crear_usuario):
    return crear_usuario(nombre="Cliente ventas")


@pytest.fixture
def api(cliente) -> APIClient:
    return api_autenticada(usuario_api(cliente))


@pytest.fixture
def variante(crear_variante):
    variante = crear_variante()
    StockVarianteModel.objects.create(
        variante=variante,
        cantidad_actual=10,
    )
    return variante


@pytest.fixture
def carrito_con_items(api, variante):
    respuesta = api.post("/api/ventas/carritos/", {}, format="json")
    carrito_id = respuesta.data["id"]
    agregado = api.post(
        f"/api/ventas/carritos/{carrito_id}/items/",
        {
            "variante_id": str(variante.id),
            "cantidad": 2,
            "precio_monto": "0.01",
        },
        format="json",
    )
    assert agregado.status_code == 201
    return carrito_id


def test_carrito_y_pedidos_requieren_autenticacion() -> None:
    api = APIClient()

    assert api.get("/api/ventas/carritos/").status_code == 401
    assert api.post("/api/ventas/carritos/", {}, format="json").status_code == 401
    assert api.get("/api/ventas/pedidos/").status_code == 401
    assert api.post("/api/ventas/pedidos/", {}, format="json").status_code == 401


def test_cliente_id_se_deriva_de_la_sesion(api, cliente, crear_usuario) -> None:
    ajeno = crear_usuario(nombre="Cliente ajeno")

    respuesta = api.post(
        "/api/ventas/carritos/",
        {"cliente_id": str(ajeno.id)},
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["cliente_id"] == str(cliente.id)


def test_precio_externo_se_ignora_y_se_usa_el_efectivo(api, variante) -> None:
    variante.precio_monto = Decimal("74.25")
    variante.precio_moneda = "PEN"
    variante.save(update_fields=["precio_monto", "precio_moneda"])
    carrito_id = api.post("/api/ventas/carritos/", {}, format="json").data["id"]

    respuesta = api.post(
        f"/api/ventas/carritos/{carrito_id}/items/",
        {
            "variante_id": str(variante.id),
            "cantidad": 1,
            "precio_monto": "0.01",
            "precio_moneda": "USD",
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["items"][0]["precio_monto"] == "74.25"
    assert respuesta.data["items"][0]["precio_moneda"] == "PEN"


@pytest.mark.parametrize("desactivar", ["variante", "prenda"])
def test_no_agrega_variantes_inactivas(api, variante, desactivar) -> None:
    if desactivar == "variante":
        variante.activa = False
        variante.save(update_fields=["activa"])
    else:
        variante.prenda.estado = "inactiva"
        variante.prenda.save(update_fields=["estado"])
    carrito_id = api.post("/api/ventas/carritos/", {}, format="json").data["id"]

    respuesta = api.post(
        f"/api/ventas/carritos/{carrito_id}/items/",
        {"variante_id": str(variante.id), "cantidad": 1},
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta.data["codigo"] == "variante_no_disponible"


def test_valida_stock_incluyendo_cantidad_ya_agregada(api, variante) -> None:
    carrito_id = api.post("/api/ventas/carritos/", {}, format="json").data["id"]
    url = f"/api/ventas/carritos/{carrito_id}/items/"
    api.post(url, {"variante_id": str(variante.id), "cantidad": 6}, format="json")

    respuesta = api.post(
        url,
        {"variante_id": str(variante.id), "cantidad": 5},
        format="json",
    )

    assert respuesta.status_code == 400
    assert respuesta.data["codigo"] == "stock_insuficiente"


def test_cliente_solo_lista_y_consulta_carritos_propios(
    api, cliente, crear_usuario
) -> None:
    propio = api.post("/api/ventas/carritos/", {}, format="json").data["id"]
    ajeno = crear_usuario(nombre="Otro cliente")
    carrito_ajeno = CarritoModel.objects.create(cliente=ajeno)

    listado = api.get("/api/ventas/carritos/")
    detalle = api.get(f"/api/ventas/carritos/{carrito_ajeno.id}/")

    assert [carrito["id"] for carrito in listado.data] == [propio]
    assert detalle.status_code == 403


def test_admin_lista_y_consulta_todos(crear_usuario) -> None:
    primero = crear_usuario(nombre="Primero")
    segundo = crear_usuario(nombre="Segundo")
    carritos = [
        CarritoModel.objects.create(cliente=primero),
        CarritoModel.objects.create(cliente=segundo),
    ]
    admin = crear_usuario(nombre="Admin", rol="Administrador")
    api = api_autenticada(usuario_api(admin, "Administrador"))

    listado = api.get("/api/ventas/carritos/")
    detalle = api.get(f"/api/ventas/carritos/{carritos[1].id}/")

    assert {item["id"] for item in listado.data} == {
        str(carrito.id) for carrito in carritos
    }
    assert detalle.status_code == 200


def test_generar_pedido_reserva_y_cancelar_libera(
    api, carrito_con_items, variante
) -> None:
    creado = api.post(
        "/api/ventas/pedidos/",
        {"carrito_id": carrito_con_items, "cliente_id": "suplantado"},
        format="json",
    )

    assert creado.status_code == 201
    assert creado.data["total_monto"] == "119.80"
    stock = StockVarianteModel.objects.get(variante=variante)
    assert stock.cantidad_reservada == 2

    cancelado = api.post(
        f"/api/ventas/pedidos/{creado.data['id']}/cancelar/",
        format="json",
    )
    stock.refresh_from_db()
    assert cancelado.status_code == 200
    assert stock.cantidad_reservada == 0


def test_doble_cancelacion_no_libera_dos_veces(
    api, carrito_con_items, variante
) -> None:
    pedido_id = api.post(
        "/api/ventas/pedidos/",
        {"carrito_id": carrito_con_items},
        format="json",
    ).data["id"]
    url = f"/api/ventas/pedidos/{pedido_id}/cancelar/"
    api.post(url, format="json")

    repetida = api.post(url, format="json")

    assert repetida.status_code == 400
    assert StockVarianteModel.objects.get(variante=variante).cantidad_reservada == 0


def test_reserva_de_todas_las_variantes_es_atomica(
    api, variante, crear_variante
) -> None:
    sin_stock = crear_variante()
    StockVarianteModel.objects.create(variante=sin_stock, cantidad_actual=0)
    carrito_id = api.post("/api/ventas/carritos/", {}, format="json").data["id"]
    url = f"/api/ventas/carritos/{carrito_id}/items/"
    api.post(url, {"variante_id": str(variante.id), "cantidad": 2}, format="json")
    # Se baja el stock despues de agregar para probar el rollback al convertir.
    api.post(
        url,
        {"variante_id": str(sin_stock.id), "cantidad": 1},
        format="json",
    )
    stock_sin = StockVarianteModel.objects.get(variante=sin_stock)
    stock_sin.cantidad_actual = 1
    stock_sin.save(update_fields=["cantidad_actual"])
    agregado = api.post(
        url,
        {"variante_id": str(sin_stock.id), "cantidad": 1},
        format="json",
    )
    assert agregado.status_code == 201
    stock_sin.cantidad_actual = 0
    stock_sin.save(update_fields=["cantidad_actual"])

    respuesta = api.post(
        "/api/ventas/pedidos/", {"carrito_id": carrito_id}, format="json"
    )

    assert respuesta.status_code == 400
    assert StockVarianteModel.objects.get(variante=variante).cantidad_reservada == 0
    assert PedidoModel.objects.count() == 0
    assert CarritoModel.objects.get(id=carrito_id).estado == "abierto"


def test_cliente_no_consulta_ni_cancela_pedido_ajeno(
    api, crear_usuario, crear_carrito
) -> None:
    ajeno = crear_usuario(nombre="Dueno pedido")
    pedido = PedidoModel.objects.create(
        cliente=ajeno,
        carrito=crear_carrito(ajeno),
        total_monto=Decimal("10.00"),
    )

    assert api.get("/api/ventas/pedidos/").data == []
    assert api.get(f"/api/ventas/pedidos/{pedido.id}/").status_code == 403
    assert api.post(f"/api/ventas/pedidos/{pedido.id}/cancelar/").status_code == 403


def test_admin_lista_y_consulta_todos_los_pedidos(
    crear_usuario, crear_carrito
) -> None:
    clientes = [crear_usuario(nombre=f"Cliente {indice}") for indice in range(2)]
    pedidos = [
        PedidoModel.objects.create(
            cliente=cliente,
            carrito=crear_carrito(cliente),
            total_monto=Decimal("10.00"),
        )
        for cliente in clientes
    ]
    admin = crear_usuario(nombre="Admin pedidos", rol="Administrador")
    api = api_autenticada(usuario_api(admin, "Administrador"))

    listado = api.get("/api/ventas/pedidos/")
    detalle = api.get(f"/api/ventas/pedidos/{pedidos[1].id}/")

    assert {item["id"] for item in listado.data} == {
        str(pedido.id) for pedido in pedidos
    }
    assert detalle.status_code == 200
