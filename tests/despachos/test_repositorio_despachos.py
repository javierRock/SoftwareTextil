"""Suite de repositorio: DjangoRepositorioDespacho contra PostgreSQL (Lab 05).

SetUp: `despacho_guardado` persiste un despacho de un pedido real.
TearDown: pytest-django revierte la transaccion al terminar cada caso.
"""

from uuid import uuid4

import pytest

from apps.compartido.domain.enums import EstadoDespacho
from apps.ventas.despachos.domain.despacho import DespachoFabrica, GuiaRemision
from apps.ventas.despachos.infrastructure.repositories import (
    DjangoRepositorioDespacho,
)


@pytest.fixture
def repo() -> DjangoRepositorioDespacho:
    return DjangoRepositorioDespacho()


@pytest.fixture
def despacho_guardado(repo, crear_pedido):
    despacho = DespachoFabrica.crear(str(crear_pedido().id), "Calle Mercaderes 200")
    repo.guardar(despacho)
    return despacho


@pytest.mark.django_db
class TestDjangoRepositorioDespacho:
    def test_guardar_y_buscar_por_pedido(self, repo, despacho_guardado) -> None:
        recuperado = repo.buscar_por_pedido(despacho_guardado.pedido_id)

        assert recuperado.id == despacho_guardado.id
        assert recuperado.estado == EstadoDespacho.PENDIENTE
        assert recuperado.guia is None

    def test_confirmar_persiste_la_guia_de_remision(
        self, repo, despacho_guardado, crear_usuario
    ) -> None:
        despacho_guardado.preparar(str(crear_usuario(rol="Encargado").id))
        despacho_guardado.confirmar(GuiaRemision("T001", "000045", "Olva"))
        repo.guardar(despacho_guardado)

        recuperado = repo.buscar_por_id(despacho_guardado.id)
        assert recuperado.estado == EstadoDespacho.CONFIRMADO
        assert recuperado.guia.codigo == "T001-000045"
        assert recuperado.guia.transportista == "Olva"

    def test_cancelar_se_refleja_en_la_base(self, repo, despacho_guardado) -> None:
        despacho_guardado.cancelar()
        repo.guardar(despacho_guardado)

        assert repo.buscar_por_id(despacho_guardado.id).estado == (
            EstadoDespacho.CANCELADO
        )

    def test_pedido_sin_despacho_devuelve_none(self, repo) -> None:
        assert repo.buscar_por_pedido(str(uuid4())) is None

    def test_id_mal_formado_devuelve_none(self, repo) -> None:
        assert repo.buscar_por_id("despacho-1") is None
