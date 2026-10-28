"""Pruebas del resumen de stock agrupado por categoria (historia SDGT-59).

Con el esquema de variantes la respuesta tiene tres niveles: la categoria
agrupa prendas y cada prenda detalla sus variantes con talla y SKU.
"""

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.inventario.infrastructure.models import (
    MovimientoInventarioModel,
    StockVarianteModel,
)

pytestmark = pytest.mark.django_db

URL = "/api/stock/por-categoria/"
CATEGORIA_INEXISTENTE = "00000000-0000-4000-8000-000000000000"


@pytest.fixture
def alta_de_stock(crear_variante):
    """Da de alta una variante con existencias y devuelve su modelo."""

    def _alta(prenda, talla: str, cantidad: int, color: str = ""):
        variante = crear_variante(prenda=prenda, talla=talla, color=color)
        StockVarianteModel.objects.create(
            variante=variante,
            cantidad_actual=cantidad,
            nivel_minimo=0,
        )
        return variante

    return _alta


def _categorias(respuesta) -> list[str]:
    return [fila["categoria"] for fila in respuesta.data]


def test_una_prenda_con_una_variante(client, prenda, alta_de_stock) -> None:
    variante = alta_de_stock(prenda, "M", 10)

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert len(respuesta.data) == 1
    categoria = respuesta.data[0]
    assert categoria["categoria"] == "Camisetas"
    assert categoria["cantidad_total"] == 10
    assert len(categoria["prendas"]) == 1
    assert categoria["prendas"][0]["cantidad"] == 10
    assert categoria["prendas"][0]["variantes"] == [
        {
            "variante_id": str(variante.id),
            "sku": variante.sku,
            "talla": "M",
            "color": "",
            "cantidad": 10,
            "cantidad_reservada": 0,
            "cantidad_disponible": 10,
        }
    ]


def test_una_prenda_agrupa_sus_variantes_y_suma_el_total(
    client,
    prenda,
    alta_de_stock,
) -> None:
    """El aporte del rediseno: la talla M y la L ya no se confunden."""
    alta_de_stock(prenda, "M", 10)
    alta_de_stock(prenda, "L", 4)

    respuesta = client.get(URL)

    categoria = respuesta.data[0]
    assert categoria["cantidad_total"] == 14
    assert len(categoria["prendas"]) == 1

    ficha = categoria["prendas"][0]
    assert ficha["cantidad"] == 14
    assert {(v["talla"], v["cantidad"]) for v in ficha["variantes"]} == {
        ("M", 10),
        ("L", 4),
    }


def test_varias_prendas_dentro_de_la_misma_categoria(
    client,
    prenda,
    crear_prenda,
    alta_de_stock,
) -> None:
    otra = crear_prenda()
    otra.categoria = prenda.categoria
    otra.save()

    alta_de_stock(prenda, "M", 10)
    alta_de_stock(otra, "S", 5)

    respuesta = client.get(URL)

    assert len(respuesta.data) == 1
    assert respuesta.data[0]["cantidad_total"] == 15
    assert len(respuesta.data[0]["prendas"]) == 2


def test_varias_categorias(client, prenda, crear_prenda, alta_de_stock) -> None:
    alta_de_stock(prenda, "M", 10)
    alta_de_stock(crear_prenda(), "S", 3)

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert len(respuesta.data) == 2
    assert "Camisetas" in _categorias(respuesta)


def test_variante_con_stock_cero_aparece_en_el_resumen(
    client,
    prenda,
    alta_de_stock,
) -> None:
    alta_de_stock(prenda, "M", 0)

    respuesta = client.get(URL)

    assert respuesta.data[0]["cantidad_total"] == 0
    assert respuesta.data[0]["prendas"][0]["cantidad"] == 0


def test_sin_existencias_devuelve_coleccion_vacia(client) -> None:
    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.data == []


def test_categoria_inexistente_devuelve_404(client) -> None:
    respuesta = client.get(URL, {"categoria_id": CATEGORIA_INEXISTENTE})

    assert respuesta.status_code == 404
    assert respuesta.data["error"] == "La categoria no existe"


def test_filtro_por_categoria_id(
    client,
    prenda,
    crear_prenda,
    alta_de_stock,
) -> None:
    alta_de_stock(prenda, "M", 10)
    alta_de_stock(crear_prenda(), "S", 3)

    respuesta = client.get(URL, {"categoria_id": str(prenda.categoria_id)})

    assert respuesta.status_code == 200
    assert len(respuesta.data) == 1
    assert respuesta.data[0]["categoria"] == "Camisetas"
    assert respuesta.data[0]["cantidad_total"] == 10


def test_el_resumen_refleja_un_ingreso(client, stock, variante_id) -> None:
    client.post(
        "/api/stock/ingresos/",
        {"variante_id": variante_id, "cantidad": 5, "motivo": "Ingreso"},
        format="json",
    )

    respuesta = client.get(URL)
    stock.refresh_from_db()

    assert stock.cantidad_actual == 15
    assert respuesta.data[0]["cantidad_total"] == 15
    assert respuesta.data[0]["prendas"][0]["cantidad"] == 15
    assert MovimientoInventarioModel.objects.count() == 1


def test_el_resumen_refleja_una_salida(client, stock, variante_id) -> None:
    client.post(
        "/api/stock/salidas/",
        {"variante_id": variante_id, "cantidad": 4, "motivo": "Salida"},
        format="json",
    )

    respuesta = client.get(URL)
    stock.refresh_from_db()

    assert stock.cantidad_actual == 6
    assert respuesta.data[0]["cantidad_total"] == 6
    assert MovimientoInventarioModel.objects.count() == 1


def test_una_salida_rechazada_no_altera_el_resumen(
    client,
    stock,
    variante_id,
) -> None:
    client.post(
        "/api/stock/salidas/",
        {"variante_id": variante_id, "cantidad": 99, "motivo": "Salida"},
        format="json",
    )

    respuesta = client.get(URL)
    stock.refresh_from_db()

    assert stock.cantidad_actual == 10
    assert respuesta.data[0]["cantidad_total"] == 10
    assert MovimientoInventarioModel.objects.count() == 0


def test_no_existe_problema_n_mas_uno(
    client,
    prenda,
    crear_prenda,
    alta_de_stock,
) -> None:
    """Recorrer stock -> variante -> prenda -> categoria no dispara consultas.

    Las claves foraneas permiten resolverlo con un solo `select_related`, asi
    que agregar prendas no debe aumentar el numero de consultas.
    """
    for talla in ("S", "M", "L"):
        alta_de_stock(prenda, talla, 5)
    for indice in range(3):
        alta_de_stock(crear_prenda(), f"T{indice}", 2)

    with CaptureQueriesContext(connection) as consultas:
        respuesta = client.get(URL)

    assert respuesta.status_code == 200
    consultas_del_resumen = [
        consulta
        for consulta in consultas.captured_queries
        if "stocks_variante" in consulta["sql"]
    ]
    assert len(consultas_del_resumen) == 1
