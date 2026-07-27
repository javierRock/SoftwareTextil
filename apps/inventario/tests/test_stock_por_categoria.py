"""Pruebas de la consulta de stock agrupado por categoria."""

from decimal import Decimal

import pytest

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel
from apps.inventario.infrastructure.models import MovimientoInventarioModel, StockPrendaModel


def _crear_categoria(categoria_id: str, nombre: str) -> CategoriaModel:
    return CategoriaModel.objects.create(id=categoria_id, nombre=nombre, descripcion=f"Categoria {nombre}")


def _crear_prenda(
    *,
    prenda_id: str,
    nombre: str,
    categoria: CategoriaModel,
    stock: int | None = None,
) -> PrendaModel:
    prenda = PrendaModel.objects.create(
        id=prenda_id,
        nombre=nombre,
        descripcion=f"{nombre} descripcion",
        precio_monto=Decimal("10.00"),
        precio_moneda="PEN",
        categoria=categoria,
        estado="activa",
        registrado_por="usuario-1",
    )
    if stock is not None:
        StockPrendaModel.objects.create(
            id=f"stock-{prenda_id}",
            prenda_id=prenda.id,
            cantidad_actual=stock,
            nivel_minimo=2,
            ubicacion="almacen",
            unidad="unidad",
        )
    return prenda


def _mapear_respuesta(respuesta):
    return sorted(respuesta.data, key=lambda item: item["categoria"])


@pytest.mark.django_db
def test_una_categoria_con_una_prenda(client) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa manga larga", categoria=categoria, stock=20)

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert respuesta.data == [
        {
            "categoria_id": "categoria-1",
            "categoria": "Camisas",
            "cantidad_total": 20,
            "prendas": [{"prenda_id": "prenda-1", "nombre": "Camisa manga larga", "cantidad": 20}],
        }
    ]


@pytest.mark.django_db
def test_una_categoria_con_varias_prendas(client) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa manga larga", categoria=categoria, stock=20)
    _crear_prenda(prenda_id="prenda-2", nombre="Camisa manga corta", categoria=categoria, stock=10)

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert respuesta.data == [
        {
            "categoria_id": "categoria-1",
            "categoria": "Camisas",
            "cantidad_total": 30,
            "prendas": [
                {"prenda_id": "prenda-2", "nombre": "Camisa manga corta", "cantidad": 10},
                {"prenda_id": "prenda-1", "nombre": "Camisa manga larga", "cantidad": 20},
            ],
        }
    ]


@pytest.mark.django_db
def test_varias_categorias(client) -> None:
    categoria_a = _crear_categoria("categoria-1", "Camisas")
    categoria_b = _crear_categoria("categoria-2", "Jeans")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa", categoria=categoria_a, stock=20)
    _crear_prenda(prenda_id="prenda-2", nombre="Jean slim", categoria=categoria_b, stock=15)

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert _mapear_respuesta(respuesta) == [
        {
            "categoria_id": "categoria-1",
            "categoria": "Camisas",
            "cantidad_total": 20,
            "prendas": [{"prenda_id": "prenda-1", "nombre": "Camisa", "cantidad": 20}],
        },
        {
            "categoria_id": "categoria-2",
            "categoria": "Jeans",
            "cantidad_total": 15,
            "prendas": [{"prenda_id": "prenda-2", "nombre": "Jean slim", "cantidad": 15}],
        },
    ]


@pytest.mark.django_db
def test_total_exacto_por_categoria(client) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa 1", categoria=categoria, stock=7)
    _crear_prenda(prenda_id="prenda-2", nombre="Camisa 2", categoria=categoria, stock=8)

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert respuesta.data[0]["cantidad_total"] == 15


@pytest.mark.django_db
def test_cantidad_exacta_por_prenda(client) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa 1", categoria=categoria, stock=7)
    _crear_prenda(prenda_id="prenda-2", nombre="Camisa 2", categoria=categoria, stock=8)

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    prendas = respuesta.data[0]["prendas"]
    assert prendas == [
        {"prenda_id": "prenda-1", "nombre": "Camisa 1", "cantidad": 7},
        {"prenda_id": "prenda-2", "nombre": "Camisa 2", "cantidad": 8},
    ]


@pytest.mark.django_db
def test_prenda_con_stock_cero(client) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa 0", categoria=categoria, stock=0)

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert respuesta.data[0]["cantidad_total"] == 0
    assert respuesta.data[0]["prendas"][0]["cantidad"] == 0


@pytest.mark.django_db
def test_categoria_sin_stock_devuelve_coleccion_vacia(client) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa sin stock", categoria=categoria, stock=None)

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert respuesta.data == []


@pytest.mark.django_db
def test_categoria_inexistente_devuelve_404(client) -> None:
    respuesta = client.get("/api/stock/por-categoria/?categoria_id=categoria-inexistente")

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "La categoria no existe"


@pytest.mark.django_db
def test_filtro_por_categoria_id(client) -> None:
    categoria_a = _crear_categoria("categoria-1", "Camisas")
    categoria_b = _crear_categoria("categoria-2", "Jeans")
    _crear_prenda(prenda_id="prenda-1", nombre="Camisa", categoria=categoria_a, stock=20)
    _crear_prenda(prenda_id="prenda-2", nombre="Jean", categoria=categoria_b, stock=15)

    respuesta = client.get("/api/stock/por-categoria/?categoria_id=categoria-2")

    assert respuesta.status_code == 200
    assert respuesta.data == [
        {
            "categoria_id": "categoria-2",
            "categoria": "Jeans",
            "cantidad_total": 15,
            "prendas": [{"prenda_id": "prenda-2", "nombre": "Jean", "cantidad": 15}],
        }
    ]


@pytest.mark.django_db
def test_respuesta_vacia(client) -> None:
    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert respuesta.data == []


@pytest.mark.django_db
def test_consulta_despues_de_registrar_un_ingreso(client, stock, prenda) -> None:
    client.post(
        "/api/stock/ingresos/",
        {"prenda_id": prenda.id, "cantidad": 5, "motivo": "Ingreso", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()
    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert stock.cantidad_actual == 15
    assert respuesta.data[0]["cantidad_total"] == 15
    assert respuesta.data[0]["prendas"][0]["cantidad"] == 15
    assert MovimientoInventarioModel.objects.count() == 1


@pytest.mark.django_db
def test_consulta_despues_de_registrar_una_salida(client, stock, prenda) -> None:
    client.post(
        "/api/stock/salidas/",
        {"prenda_id": prenda.id, "cantidad": 4, "motivo": "Salida", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()
    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert stock.cantidad_actual == 6
    assert respuesta.data[0]["cantidad_total"] == 6
    assert respuesta.data[0]["prendas"][0]["cantidad"] == 6
    assert MovimientoInventarioModel.objects.count() == 1


@pytest.mark.django_db
def test_consulta_despues_de_una_salida_rechazada(client, stock, prenda) -> None:
    client.post(
        "/api/stock/salidas/",
        {"prenda_id": prenda.id, "cantidad": 50, "motivo": "Salida", "usuario_id": "usuario-1"},
        format="json",
    )

    stock.refresh_from_db()
    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert stock.cantidad_actual == 10
    assert respuesta.data[0]["cantidad_total"] == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_get_no_modifica_la_base_de_datos(client, stock, prenda) -> None:
    stock_count_before = StockPrendaModel.objects.count()
    movement_count_before = MovimientoInventarioModel.objects.count()

    respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert StockPrendaModel.objects.count() == stock_count_before
    assert MovimientoInventarioModel.objects.count() == movement_count_before


@pytest.mark.django_db
def test_no_existe_problema_n_mas_uno(client, django_assert_num_queries) -> None:
    categoria = _crear_categoria("categoria-1", "Camisas")
    for indice in range(5):
        _crear_prenda(prenda_id=f"prenda-{indice}", nombre=f"Camisa {indice}", categoria=categoria, stock=indice + 1)

    with django_assert_num_queries(2):
        respuesta = client.get("/api/stock/por-categoria/")

    assert respuesta.status_code == 200
    assert respuesta.data[0]["cantidad_total"] == 15
