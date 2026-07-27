import pytest
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import (
    CategoriaModel,
    PrendaModel,
    TipoProductoModel,
)

pytestmark = pytest.mark.django_db


def _crear_prenda():
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    tipo = TipoProductoModel.objects.create(nombre="Camisa")
    prenda = PrendaModel.objects.create(
        nombre="Camisa clasica",
        descripcion="Algodon",
        precio_monto="49.90",
        categoria=categoria,
        tipo_producto=tipo,
        estado="activa",
    )
    return prenda, categoria, tipo


def test_api_desactiva_y_activa_sin_eliminar_ni_romper_referencias(
    cliente_admin,
) -> None:
    prenda, categoria, tipo = _crear_prenda()
    cliente, _ = cliente_admin

    desactivacion = cliente.post(f"/api/prendas/{prenda.id}/desactivar/")
    assert desactivacion.status_code == 200
    assert desactivacion.data["estado"] == "inactiva"

    prenda.refresh_from_db()
    assert prenda.estado == "inactiva"
    assert prenda.categoria_id == categoria.id
    assert prenda.tipo_producto_id == tipo.id
    assert PrendaModel.objects.filter(id=prenda.id).exists()
    publico = APIClient()
    assert publico.get("/api/prendas/").data == []

    activacion = cliente.post(f"/api/prendas/{prenda.id}/activar/")
    assert activacion.status_code == 200
    assert activacion.data["estado"] == "activa"

    prenda.refresh_from_db()
    assert prenda.estado == "activa"
    assert prenda.categoria_id == categoria.id
    assert prenda.tipo_producto_id == tipo.id
    assert [item["id"] for item in publico.get("/api/prendas/").data] == [
        str(prenda.id)
    ]


@pytest.mark.parametrize("accion", ["activar", "desactivar"])
def test_api_controla_publicacion_de_prenda_inexistente(
    accion,
    cliente_admin,
) -> None:
    cliente, _ = cliente_admin
    respuesta = cliente.post(f"/api/prendas/inexistente/{accion}/")

    assert respuesta.status_code == 404
    assert "error" in respuesta.data


def test_api_no_permite_eliminacion_fisica_de_prenda(cliente_admin) -> None:
    prenda, categoria, tipo = _crear_prenda()
    cliente, _ = cliente_admin

    respuesta = cliente.delete(f"/api/prendas/{prenda.id}/")

    assert respuesta.status_code == 405
    prenda.refresh_from_db()
    assert prenda.categoria_id == categoria.id
    assert prenda.tipo_producto_id == tipo.id
