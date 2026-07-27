"""Pruebas del modulo de pedidos que evidencian LSP, ISP y DIP.

`ServicioPedidos` se arma con dobles en memoria en lugar de los repositorios
Django: la prueba pasa sin base de datos porque el servicio depende de los
contratos del dominio.
"""

import pytest

from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.carrito.application.services import ServicioCompras
from apps.ventas.carrito.domain.errors import CarritoCerradoError
from apps.ventas.carrito.infrastructure.memoria import MemoriaRepositorioCarrito
from apps.ventas.pedidos.application.consultas import ConsultaPedidos
from apps.ventas.pedidos.application.services import ServicioPedidos
from apps.ventas.pedidos.domain.errors import (
    CarritoNoEncontradoError,
    CarritoNoPerteneceAClienteError,
    PedidoNoEncontradoError,
    PedidoSinDetallesError,
)
from apps.ventas.pedidos.infrastructure.memoria import MemoriaRepositorioPedido

CLIENTE = "cliente-1"


@pytest.fixture
def repo_carrito() -> MemoriaRepositorioCarrito:
    return MemoriaRepositorioCarrito()


@pytest.fixture
def repo_pedido() -> MemoriaRepositorioPedido:
    return MemoriaRepositorioPedido()


@pytest.fixture
def servicio_compras(repo_carrito) -> ServicioCompras:
    return ServicioCompras(lector=repo_carrito, escritor=repo_carrito)


@pytest.fixture
def servicio(repo_pedido, repo_carrito) -> ServicioPedidos:
    return ServicioPedidos(
        lector_pedido=repo_pedido,
        escritor_pedido=repo_pedido,
        lector_carrito=repo_carrito,
        escritor_carrito=repo_carrito,
    )


@pytest.fixture
def consulta(repo_pedido) -> ConsultaPedidos:
    return ConsultaPedidos(lector=repo_pedido, catalogo=repo_pedido)


def _carrito_con_items(servicio_compras, cliente_id: str = CLIENTE):
    carrito = servicio_compras.crear_carrito(cliente_id=cliente_id)
    servicio_compras.agregar_item(carrito.id, "prenda-1", 2, "30.00")
    servicio_compras.agregar_item(carrito.id, "prenda-2", 1, "40.00")
    return carrito


def test_generar_pedido_desde_carrito(servicio, servicio_compras, consulta):
    carrito = _carrito_con_items(servicio_compras)

    pedido = servicio.generar_desde_carrito(carrito.id, CLIENTE)

    assert pedido.estado is EstadoPedido.CREADO
    assert pedido.total.monto == 100
    assert len(pedido.detalles) == 2
    assert consulta.obtener(pedido.id).id == pedido.id


def test_el_carrito_queda_convertido_y_no_genera_un_segundo_pedido(
    servicio, servicio_compras
):
    carrito = _carrito_con_items(servicio_compras)
    servicio.generar_desde_carrito(carrito.id, CLIENTE)

    with pytest.raises(CarritoCerradoError):
        servicio.generar_desde_carrito(carrito.id, CLIENTE)


def test_no_se_genera_pedido_de_carrito_ajeno(servicio, servicio_compras):
    carrito = _carrito_con_items(servicio_compras, cliente_id="otro-cliente")

    with pytest.raises(CarritoNoPerteneceAClienteError):
        servicio.generar_desde_carrito(carrito.id, CLIENTE)


def test_no_se_genera_pedido_de_carrito_vacio(servicio, servicio_compras):
    """La fabrica rechaza el pedido sin detalles antes de tocar el carrito."""
    carrito = servicio_compras.crear_carrito(cliente_id=CLIENTE)

    with pytest.raises(PedidoSinDetallesError):
        servicio.generar_desde_carrito(carrito.id, CLIENTE)


def test_carrito_inexistente(servicio):
    with pytest.raises(CarritoNoEncontradoError):
        servicio.generar_desde_carrito("carrito-fantasma", CLIENTE)


def test_cancelar_pedido(servicio, servicio_compras, consulta):
    carrito = _carrito_con_items(servicio_compras)
    pedido = servicio.generar_desde_carrito(carrito.id, CLIENTE)

    servicio.cancelar(pedido.id)

    assert consulta.obtener(pedido.id).estado is EstadoPedido.CANCELADO


def test_cancelar_pedido_inexistente(servicio):
    with pytest.raises(PedidoNoEncontradoError):
        servicio.cancelar("pedido-fantasma")


def test_consulta_filtra_por_cliente(servicio, servicio_compras, consulta):
    servicio.generar_desde_carrito(_carrito_con_items(servicio_compras).id, CLIENTE)
    otro = _carrito_con_items(servicio_compras, cliente_id="cliente-2")
    servicio.generar_desde_carrito(otro.id, "cliente-2")

    assert len(consulta.listar()) == 2
    assert len(consulta.listar(CLIENTE)) == 1
