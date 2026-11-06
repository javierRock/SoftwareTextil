"""Suite de repositorio: DjangoRepositorioPedido contra PostgreSQL (Lab 05).

Pruebas de integracion del adaptador de persistencia. pytest-django envuelve
cada caso en una transaccion que se revierte al terminar (TearDown), por lo
que la base de pruebas queda limpia entre casos.
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.pedidos.domain.pedido import DetallePedido, PedidoFactory
from apps.ventas.pedidos.infrastructure.repositories import DjangoRepositorioPedido


@pytest.fixture
def repositorio() -> DjangoRepositorioPedido:
    return DjangoRepositorioPedido()


@pytest.fixture
def pedido_nuevo(crear_usuario, crear_carrito, crear_variante):
    """SetUp: filas reales de cliente, carrito y variante para las claves foraneas."""

    def _crear(cliente=None):
        cliente = cliente or crear_usuario()
        carrito = crear_carrito(cliente)
        variante = crear_variante()
        detalle = DetallePedido(str(variante.id), 3, Dinero(Decimal("20.00")))
        return PedidoFactory.crear(str(cliente.id), str(carrito.id), [detalle])

    return _crear


@pytest.mark.django_db
class TestDjangoRepositorioPedido:
    def test_guardar_y_recuperar_pedido_con_detalles(
        self, repositorio, pedido_nuevo
    ) -> None:
        pedido = pedido_nuevo()

        repositorio.guardar(pedido)
        recuperado = repositorio.buscar_por_id(pedido.id)

        assert recuperado is not None
        assert recuperado.total == Dinero(Decimal("60.00"))
        assert recuperado.estado == EstadoPedido.CREADO
        assert len(recuperado.detalles) == 1
        assert recuperado.detalles[0].cantidad == 3

    def test_guardar_actualiza_estado_de_pedido_existente(
        self, repositorio, pedido_nuevo
    ) -> None:
        pedido = pedido_nuevo()
        repositorio.guardar(pedido)

        pedido.cancelar()
        repositorio.guardar(pedido)

        recuperado = repositorio.buscar_por_id(pedido.id)
        assert recuperado.estado == EstadoPedido.CANCELADO
        assert len(recuperado.detalles) == 1

    def test_buscar_id_inexistente_devuelve_none(self, repositorio) -> None:
        assert repositorio.buscar_por_id(str(uuid4())) is None

    def test_buscar_id_mal_formado_devuelve_none(self, repositorio) -> None:
        assert repositorio.buscar_por_id("no-es-un-uuid") is None

    def test_listar_por_cliente_solo_devuelve_sus_pedidos(
        self, repositorio, pedido_nuevo, crear_usuario
    ) -> None:
        cliente = crear_usuario()
        propio = pedido_nuevo(cliente)
        ajeno = pedido_nuevo()
        repositorio.guardar(propio)
        repositorio.guardar(ajeno)

        pedidos = repositorio.listar_por_cliente(str(cliente.id))

        assert [p.id for p in pedidos] == [propio.id]
