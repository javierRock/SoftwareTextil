import pytest
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel

pytestmark = pytest.mark.django_db


def test_api_crea_consulta_lista_y_actualiza_categoria() -> None:
    cliente = APIClient()

    creacion = cliente.post(
        "/api/categorias/",
        {"nombre": "Camisas", "descripcion": "Prendas superiores"},
        format="json",
    )
    assert creacion.status_code == 201
    categoria_id = creacion.data["id"]

    detalle = cliente.get(f"/api/categorias/{categoria_id}/")
    assert detalle.status_code == 200
    assert detalle.data["nombre"] == "Camisas"

    actualizacion = cliente.patch(
        f"/api/categorias/{categoria_id}/",
        {"descripcion": "Camisas y blusas"},
        format="json",
    )
    assert actualizacion.status_code == 200
    assert actualizacion.data == {
        "id": categoria_id,
        "nombre": "Camisas",
        "descripcion": "Camisas y blusas",
    }

    listado = cliente.get("/api/categorias/")
    assert listado.status_code == 200
    assert [categoria["id"] for categoria in listado.data] == [categoria_id]


def test_api_rechaza_categoria_invalida_sin_persistirla() -> None:
    cliente = APIClient()

    respuesta = cliente.post(
        "/api/categorias/",
        {"nombre": "   ", "descripcion": "Invalida"},
        format="json",
    )

    assert respuesta.status_code == 400
    assert CategoriaModel.objects.count() == 0


def test_api_controla_categoria_inexistente() -> None:
    cliente = APIClient()

    assert cliente.get("/api/categorias/inexistente/").status_code == 404
    assert (
        cliente.patch(
            "/api/categorias/inexistente/",
            {"nombre": "Camisas"},
            format="json",
        ).status_code
        == 404
    )


def test_api_no_elimina_categoria_referenciada_por_una_prenda() -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    PrendaModel.objects.create(
        nombre="Camisa clasica",
        precio_monto="49.90",
        categoria=categoria,
    )
    cliente = APIClient()

    respuesta = cliente.delete(f"/api/categorias/{categoria.id}/")

    assert respuesta.status_code == 405
    assert CategoriaModel.objects.filter(id=categoria.id).exists()
    assert PrendaModel.objects.filter(categoria_id=categoria.id).exists()
