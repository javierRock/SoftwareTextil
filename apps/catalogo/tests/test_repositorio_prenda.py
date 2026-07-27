from decimal import Decimal

import pytest

from apps.catalogo.domain.prenda import PrendaFabrica
from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel
from apps.catalogo.infrastructure.repositories import DjangoRepositorioPrenda
from apps.compartido.domain.dinero import Dinero

pytestmark = pytest.mark.django_db


def test_repositorio_persiste_y_recupera_la_ficha_comercial(crear_usuario) -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    usuario = crear_usuario()
    prenda = PrendaFabrica.crear(
        nombre="Camisa clasica",
        descripcion="Algodon",
        precio=Dinero(Decimal("49.90"), "PEN"),
        categoria_id=str(categoria.id),
        tallas=["M", "40"],
        registrado_por=str(usuario.id),
    )
    repositorio = DjangoRepositorioPrenda()

    repositorio.guardar(prenda)
    recuperada = repositorio.buscar_por_id(prenda.id)

    assert recuperada is not None
    assert recuperada.id == prenda.id
    assert recuperada.nombre == prenda.nombre
    assert recuperada.descripcion == prenda.descripcion
    assert recuperada.precio == prenda.precio
    assert recuperada.categoria_id == prenda.categoria_id
    assert recuperada.tallas == ["M", "40"]
    assert recuperada.registrado_por == prenda.registrado_por
    assert PrendaModel.objects.count() == 1
