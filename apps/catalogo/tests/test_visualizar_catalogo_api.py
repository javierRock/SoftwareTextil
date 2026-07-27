import pytest
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel, TipoProductoModel


pytestmark = pytest.mark.django_db


def test_api_devuelve_catalogo_vacio() -> None:
    respuesta = APIClient().get("/api/prendas/")

    assert respuesta.status_code == 200
    assert respuesta.data == []


def test_api_serializa_datos_comerciales_de_prendas_visibles() -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    tipo = TipoProductoModel.objects.create(nombre="Camisa")
    visible = PrendaModel.objects.create(
        nombre="Camisa clasica",
        descripcion="Algodon",
        precio_monto="49.90",
        precio_moneda="PEN",
        categoria=categoria,
        tipo_producto=tipo,
        estado="activa",
    )
    PrendaModel.objects.create(
        nombre="Camisa retirada",
        descripcion="No visible",
        precio_monto="39.90",
        precio_moneda="PEN",
        categoria=categoria,
        estado="inactiva",
    )

    respuesta = APIClient().get("/api/prendas/")

    assert respuesta.status_code == 200
    assert respuesta.data == [
        {
            "id": str(visible.id),
            "nombre": "Camisa clasica",
            "descripcion": "Algodon",
            "precio_monto": "49.90",
            "precio_moneda": "PEN",
            "categoria_id": str(categoria.id),
            "tipo_producto_id": str(tipo.id),
            "tallas": [],
            "estado": "activa",
        }
    ]
    assert not {
        "stock",
        "cantidad_disponible",
        "ubicacion",
        "alertas",
    }.intersection(respuesta.data[0])
