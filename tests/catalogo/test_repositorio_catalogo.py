"""Suite de repositorio: prendas y variantes contra PostgreSQL (Lab 05).

SetUp: la fixture `prenda_guardada` persiste una prenda con dos tallas.
TearDown: pytest-django revierte la transaccion al terminar cada caso.
"""

from decimal import Decimal

import pytest

from apps.catalogo.domain.prenda import PrendaFabrica, VarianteFabrica
from apps.catalogo.infrastructure.repositories import (
    DjangoRepositorioPrenda,
    DjangoRepositorioVariante,
)
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


@pytest.fixture
def repo_prendas() -> DjangoRepositorioPrenda:
    return DjangoRepositorioPrenda()


@pytest.fixture
def prenda_guardada(repo_prendas, crear_categoria):
    prenda = PrendaFabrica.crear(
        nombre="Casaca denim",
        descripcion="Casaca azul",
        precio=Dinero(Decimal("120.00")),
        categoria_id=str(crear_categoria().id),
        registrado_por=None,
        tallas=["S", "M"],
    )
    repo_prendas.guardar(prenda)
    return prenda


@pytest.mark.django_db
class TestDjangoRepositorioPrenda:
    def test_guardar_y_recuperar_con_variantes(
        self, repo_prendas, prenda_guardada
    ) -> None:
        recuperada = repo_prendas.buscar_por_id(prenda_guardada.id)

        assert recuperada.nombre == "Casaca denim"
        assert sorted(recuperada.tallas) == ["M", "S"]

    def test_quitar_variante_la_elimina_de_la_tabla(
        self, repo_prendas, prenda_guardada
    ) -> None:
        prenda_guardada.definir_variantes(["L"])
        repo_prendas.guardar(prenda_guardada)

        assert repo_prendas.buscar_por_id(prenda_guardada.id).tallas == ["L"]

    def test_listar_visibles_excluye_prendas_inactivas(
        self, repo_prendas, prenda_guardada
    ) -> None:
        prenda_guardada.desactivar()
        repo_prendas.guardar(prenda_guardada)

        visibles = [p.id for p in repo_prendas.listar_visibles()]
        assert prenda_guardada.id not in visibles

    def test_buscar_por_texto_en_descripcion(
        self, repo_prendas, prenda_guardada
    ) -> None:
        encontradas = repo_prendas.buscar(
            texto="AZUL",
            categoria_id=None,
            tipo_producto_id=None,
            estado=EstadoPrenda.ACTIVA,
        )
        assert prenda_guardada.id in [p.id for p in encontradas]

    def test_id_mal_formado_devuelve_none(self, repo_prendas) -> None:
        assert repo_prendas.buscar_por_id("123") is None


@pytest.mark.django_db
class TestDjangoRepositorioVariante:
    def test_precio_efectivo_propio_o_heredado(
        self, repo_prendas, prenda_guardada
    ) -> None:
        con_precio = VarianteFabrica.crear(
            prenda_guardada.id, "XL", precio=Dinero(Decimal("135.00"))
        )
        prenda_guardada.agregar_variante(con_precio)
        repo_prendas.guardar(prenda_guardada)
        repo = DjangoRepositorioVariante()
        sin_precio = prenda_guardada.variantes[0]

        assert repo.precio_efectivo(con_precio.id) == Dinero(Decimal("135.00"))
        assert repo.precio_efectivo(sin_precio.id) == Dinero(Decimal("120.00"))

    def test_buscar_por_sku_ignora_mayusculas(self, prenda_guardada) -> None:
        variante = prenda_guardada.variantes[0]
        encontrada = DjangoRepositorioVariante().buscar_por_sku(variante.sku.lower())
        assert encontrada.id == variante.id
