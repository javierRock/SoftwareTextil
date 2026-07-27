import pytest
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel, TipoProductoModel


pytestmark = pytest.mark.django_db


def test_api_configura_tipo_producto_sin_acceder_directamente_al_orm() -> None:
    cliente = APIClient()

    creacion = cliente.post(
        "/api/tipos-producto/",
        {"nombre": "Camisa", "atributos_base": {"manga": "corta"}},
        format="json",
    )
    assert creacion.status_code == 201
    tipo_id = creacion.data["id"]
    assert creacion.data["activo"] is True

    detalle = cliente.get(f"/api/tipos-producto/{tipo_id}/")
    assert detalle.status_code == 200
    assert detalle.data["nombre"] == "Camisa"

    actualizacion = cliente.patch(
        f"/api/tipos-producto/{tipo_id}/",
        {"nombre": "Camisa formal"},
        format="json",
    )
    assert actualizacion.status_code == 200
    assert actualizacion.data["nombre"] == "Camisa formal"
    assert actualizacion.data["atributos_base"] == {"manga": "corta"}

    desactivacion = cliente.post(f"/api/tipos-producto/{tipo_id}/desactivar/")
    assert desactivacion.status_code == 200
    assert desactivacion.data["activo"] is False

    activacion = cliente.post(f"/api/tipos-producto/{tipo_id}/activar/")
    assert activacion.status_code == 200
    assert activacion.data["activo"] is True

    listado = cliente.get("/api/tipos-producto/")
    assert listado.status_code == 200
    assert [tipo["id"] for tipo in listado.data] == [tipo_id]


def test_api_rechaza_entradas_invalidas() -> None:
    cliente = APIClient()

    respuesta = cliente.post(
        "/api/tipos-producto/",
        {"nombre": "   ", "atributos_base": {}},
        format="json",
    )

    assert respuesta.status_code == 400
    assert TipoProductoModel.objects.count() == 0


def test_api_controla_tipo_inexistente() -> None:
    cliente = APIClient()

    assert cliente.get("/api/tipos-producto/inexistente/").status_code == 404
    assert (
        cliente.patch(
            "/api/tipos-producto/inexistente/",
            {"nombre": "Camisa"},
            format="json",
        ).status_code
        == 404
    )
    assert cliente.post("/api/tipos-producto/inexistente/desactivar/").status_code == 404


def test_api_no_permite_eliminacion_fisica_de_tipos_referenciados() -> None:
    tipo = TipoProductoModel.objects.create(nombre="Camisa")
    categoria = CategoriaModel.objects.create(nombre="Ropa")
    PrendaModel.objects.create(
        nombre="Camisa clasica",
        precio_monto="49.90",
        categoria=categoria,
        tipo_producto=tipo,
    )
    cliente = APIClient()

    respuesta = cliente.delete(f"/api/tipos-producto/{tipo.id}/")

    assert respuesta.status_code == 405
    assert TipoProductoModel.objects.filter(id=tipo.id).exists()
