import pytest
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel, TipoProductoModel


pytestmark = pytest.mark.django_db


def test_api_devuelve_detalle_comercial_de_prenda_existente() -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    tipo = TipoProductoModel.objects.create(nombre="Camisa")
    prenda = PrendaModel.objects.create(
        nombre="Camisa clasica",
        descripcion="Algodon",
        precio_monto="49.90",
        precio_moneda="PEN",
        categoria=categoria,
        tipo_producto=tipo,
        estado="activa",
    )

    respuesta = APIClient().get(f"/api/prendas/{prenda.id}/")

    assert respuesta.status_code == 200
    assert respuesta.data == {
        "id": str(prenda.id),
        "nombre": "Camisa clasica",
        "descripcion": "Algodon",
        "precio_monto": "49.90",
        "precio_moneda": "PEN",
        "categoria_id": str(categoria.id),
        "tipo_producto_id": str(tipo.id),
        "estado": "activa",
    }
    assert not {
        "stock",
        "cantidad_disponible",
        "ubicacion",
        "alertas",
        "carrito",
        "pedidos",
        "ventas",
    }.intersection(respuesta.data)


def test_api_devuelve_error_controlado_para_prenda_inexistente() -> None:
    respuesta = APIClient().get("/api/prendas/inexistente/")

    assert respuesta.status_code == 404
    assert respuesta.data == {"error": "Prenda no encontrada"}
