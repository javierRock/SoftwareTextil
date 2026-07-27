import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import (
    CategoriaModel,
    PrendaModel,
    TipoProductoModel,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def prendas_busqueda():
    categoria_camisas = CategoriaModel.objects.create(nombre="Camisas")
    categoria_polos = CategoriaModel.objects.create(nombre="Polos")
    tipo_camisa = TipoProductoModel.objects.create(nombre="Camisa")
    tipo_polo = TipoProductoModel.objects.create(nombre="Polo")
    camisa = PrendaModel.objects.create(
        nombre="Camisa clasica",
        descripcion="Algodon pima",
        precio_monto="49.90",
        categoria=categoria_camisas,
        tipo_producto=tipo_camisa,
        estado="activa",
    )
    polo = PrendaModel.objects.create(
        nombre="Polo basico",
        descripcion="Prenda de algodon",
        precio_monto="29.90",
        categoria=categoria_polos,
        tipo_producto=tipo_polo,
        estado="activa",
    )
    inactiva = PrendaModel.objects.create(
        nombre="Camisa retirada",
        descripcion="Seda",
        precio_monto="39.90",
        categoria=categoria_camisas,
        tipo_producto=tipo_camisa,
        estado="inactiva",
    )
    return {
        "camisa": camisa,
        "polo": polo,
        "inactiva": inactiva,
        "categoria_camisas": categoria_camisas,
        "tipo_camisa": tipo_camisa,
    }


@pytest.mark.parametrize(
    ("parametros", "esperados"),
    [
        ({"texto": "CLASICA"}, ["camisa"]),
        ({"texto": "algodon"}, ["camisa", "polo"]),
        ({"categoria_id": "categoria"}, ["camisa"]),
        ({"tipo_producto_id": "tipo"}, ["camisa"]),
        ({"estado": "inactiva"}, ["inactiva"]),
    ],
)
def test_api_busca_por_cada_criterio(prendas_busqueda, parametros, esperados) -> None:
    if parametros.get("categoria_id"):
        parametros["categoria_id"] = str(prendas_busqueda["categoria_camisas"].id)
    if parametros.get("tipo_producto_id"):
        parametros["tipo_producto_id"] = str(prendas_busqueda["tipo_camisa"].id)

    respuesta = APIClient().get("/api/prendas/", parametros)

    assert respuesta.status_code == 200
    assert [item["id"] for item in respuesta.data] == [
        str(prendas_busqueda[nombre].id) for nombre in esperados
    ]


def test_api_combina_filtros_y_no_consulta_inventario(prendas_busqueda) -> None:
    parametros = {
        "texto": "algodon",
        "categoria_id": str(prendas_busqueda["categoria_camisas"].id),
        "tipo_producto_id": str(prendas_busqueda["tipo_camisa"].id),
        "estado": "activa",
    }

    with CaptureQueriesContext(connection) as consultas:
        respuesta = APIClient().get("/api/prendas/", parametros)

    assert respuesta.status_code == 200
    assert [item["id"] for item in respuesta.data] == [
        str(prendas_busqueda["camisa"].id)
    ]
    sql = " ".join(consulta["sql"].lower() for consulta in consultas.captured_queries)
    assert "stocks_prenda" not in sql
    assert "movimientos_inventario" not in sql
    assert "alertas_stock" not in sql


def test_api_filtros_vacios_conservan_listado_visible(prendas_busqueda) -> None:
    respuesta = APIClient().get(
        "/api/prendas/",
        {"texto": "", "categoria_id": "", "tipo_producto_id": "", "estado": ""},
    )

    assert respuesta.status_code == 200
    assert [item["id"] for item in respuesta.data] == [
        str(prendas_busqueda["camisa"].id),
        str(prendas_busqueda["polo"].id),
    ]


@pytest.mark.parametrize(
    "parametros",
    [
        {"estado": "agotada"},
        {"categoria_id": "x" * 37},
        {"tipo_producto_id": "x" * 37},
        {"stock": "10"},
    ],
)
def test_api_rechaza_parametros_invalidos(parametros) -> None:
    respuesta = APIClient().get("/api/prendas/", parametros)

    assert respuesta.status_code == 400
