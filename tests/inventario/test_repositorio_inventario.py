"""Suite de repositorio: stock, movimientos y alertas contra PostgreSQL (Lab 05).

SetUp: `stock_guardado` crea una variante real y persiste su stock.
TearDown: la transaccion de cada caso se revierte al terminar.
"""

import pytest

from apps.compartido.domain.enums import EstadoAlerta
from apps.inventario.domain.stock_prenda import InventarioFabrica
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioAlertaStock,
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)


@pytest.fixture
def repo() -> DjangoRepositorioInventario:
    return DjangoRepositorioInventario()


@pytest.fixture
def stock_guardado(repo, crear_variante):
    stock = InventarioFabrica.crear(str(crear_variante().id), 10, 5)
    repo.guardar(stock)
    return stock


@pytest.mark.django_db
class TestDjangoRepositorioInventario:
    def test_guardar_y_buscar_por_variante(self, repo, stock_guardado) -> None:
        recuperado = repo.buscar_por_variante(stock_guardado.variante_id)

        assert recuperado.id == stock_guardado.id
        assert recuperado.cantidad_actual == 10

    def test_guardar_persiste_la_reserva(self, repo, stock_guardado) -> None:
        stock_guardado.reservar(3)
        repo.guardar(stock_guardado)

        recuperado = repo.buscar_por_id(stock_guardado.id)
        assert recuperado.cantidad_reservada == 3
        assert recuperado.cantidad_disponible == 7

    def test_listar_bajo_minimo_incluye_solo_variantes_bajo_el_minimo(
        self, repo, stock_guardado, crear_variante
    ) -> None:
        bajo = InventarioFabrica.crear(str(crear_variante().id), 1, 5)
        repo.guardar(bajo)

        ids = [item.variante_id for item in repo.listar_bajo_minimo()]

        assert bajo.variante_id in ids
        assert stock_guardado.variante_id not in ids

    def test_variante_mal_formada_devuelve_none(self, repo) -> None:
        assert repo.buscar_por_variante("xyz") is None


@pytest.mark.django_db
class TestDjangoRepositorioMovimientosYAlertas:
    def test_movimientos_se_listan_por_stock(
        self, stock_guardado, crear_usuario
    ) -> None:
        usuario_id = str(crear_usuario().id)
        repo_mov = DjangoRepositorioMovimiento()
        repo_mov.guardar(stock_guardado.registrar_ingreso(2, "compra", usuario_id))
        repo_mov.guardar(stock_guardado.registrar_salida(1, "venta", usuario_id))

        movimientos = repo_mov.listar_por_stock(stock_guardado.id)

        assert len(movimientos) == 2
        assert {m.motivo for m in movimientos} == {"compra", "venta"}

    def test_alerta_atendida_deja_de_ser_pendiente(self, repo, stock_guardado) -> None:
        stock_guardado.registrar_salida(8, "venta", "u")
        repo.guardar(stock_guardado)
        alerta = stock_guardado.generar_alerta_si_corresponde()
        repo_alertas = DjangoRepositorioAlertaStock()
        repo_alertas.guardar(alerta)
        assert repo_alertas.buscar_pendiente_por_stock(stock_guardado.id) is not None

        alerta.atender()
        repo_alertas.guardar(alerta)

        assert alerta.estado == EstadoAlerta.ATENDIDA
        assert repo_alertas.buscar_pendiente_por_stock(stock_guardado.id) is None
