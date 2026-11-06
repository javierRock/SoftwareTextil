"""Suite de servicio de aplicacion: ServicioPedidos con dobles de prueba (Lab 05).

Los repositorios se sustituyen por mocks con `create_autospec`, que respetan la
firma del contrato del dominio: si el servicio llamara a un metodo inexistente
la prueba fallaria. Se verifica tanto el resultado como las interacciones.
"""

from decimal import Decimal
from unittest.mock import MagicMock, call, create_autospec

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoCarrito, EstadoPedido
from apps.inventario.domain.excepciones import StockNoEncontradoError
from apps.inventario.domain.repositorios import RepositorioInventario
from apps.inventario.domain.stock_prenda import StockVariante
from apps.ventas.carrito.domain.carrito import CarritoCompras
from apps.ventas.carrito.domain.repositorios import EscritorCarrito, LectorCarrito
from apps.ventas.pedidos.application.services import ServicioPedidos
from apps.ventas.pedidos.domain.errors import (
    CarritoNoPerteneceAClienteError,
    PedidoNoEncontradoError,
    PedidoNoPerteneceAClienteError,
)
from apps.ventas.pedidos.domain.pedido import DetallePedido, PedidoFactory
from apps.ventas.pedidos.domain.repositorios import EscritorPedido, LectorPedido

CLIENTE = "cliente-1"


class TestServicioPedidosConMocks:
    def setup_method(self) -> None:
        self.lector_pedido = create_autospec(LectorPedido, instance=True)
        self.escritor_pedido = create_autospec(EscritorPedido, instance=True)
        self.lector_carrito = create_autospec(LectorCarrito, instance=True)
        self.escritor_carrito = create_autospec(EscritorCarrito, instance=True)
        self.inventario = create_autospec(RepositorioInventario, instance=True)
        self.unidad_trabajo = MagicMock()
        self.servicio = ServicioPedidos(
            self.lector_pedido,
            self.escritor_pedido,
            self.lector_carrito,
            self.escritor_carrito,
            inventario=self.inventario,
            unidad_trabajo=self.unidad_trabajo,
        )

    @staticmethod
    def _carrito(cliente_id: str = CLIENTE) -> CarritoCompras:
        carrito = CarritoCompras(id="carrito-1", cliente_id=cliente_id)
        carrito.agregar_item("variante-b", 1, Dinero(Decimal("15.00")))
        carrito.agregar_item("variante-a", 2, Dinero(Decimal("10.00")))
        return carrito

    def test_generar_pedido_reserva_stock_y_persiste(self) -> None:
        carrito = self._carrito()
        self.lector_carrito.buscar_por_id_para_actualizar.return_value = carrito
        stock = create_autospec(StockVariante, instance=True)
        self.inventario.buscar_por_variante_bloqueada.return_value = stock

        pedido = self.servicio.generar_desde_carrito("carrito-1", CLIENTE)

        assert pedido.total == Dinero(Decimal("35.00"))
        assert carrito.estado == EstadoCarrito.CONVERTIDO
        # Las reservas se hacen en orden de variante para evitar interbloqueos.
        assert self.inventario.buscar_por_variante_bloqueada.call_args_list == [
            call("variante-a"),
            call("variante-b"),
        ]
        stock.reservar.assert_has_calls([call(2), call(1)])
        self.escritor_pedido.guardar.assert_called_once_with(pedido)
        self.escritor_carrito.guardar.assert_called_once_with(carrito)
        self.unidad_trabajo.return_value.__enter__.assert_called_once()

    def test_carrito_ajeno_no_genera_pedido_ni_reservas(self) -> None:
        self.lector_carrito.buscar_por_id_para_actualizar.return_value = self._carrito(
            "otro-cliente"
        )

        with pytest.raises(CarritoNoPerteneceAClienteError):
            self.servicio.generar_desde_carrito("carrito-1", CLIENTE)

        self.inventario.buscar_por_variante_bloqueada.assert_not_called()
        self.escritor_pedido.guardar.assert_not_called()

    def test_variante_sin_stock_aborta_sin_guardar_pedido(self) -> None:
        self.lector_carrito.buscar_por_id_para_actualizar.return_value = self._carrito()
        self.inventario.buscar_por_variante_bloqueada.return_value = None

        with pytest.raises(StockNoEncontradoError):
            self.servicio.generar_desde_carrito("carrito-1", CLIENTE)

        self.escritor_pedido.guardar.assert_not_called()
        self.escritor_carrito.guardar.assert_not_called()

    def test_cancelar_pedido_libera_reserva_y_guarda(self) -> None:
        pedido = PedidoFactory.crear(
            CLIENTE, "carrito-1", [DetallePedido("variante-a", 4, Dinero(Decimal(5)))]
        )
        self.lector_pedido.buscar_por_id_para_actualizar.return_value = pedido
        stock = create_autospec(StockVariante, instance=True)
        self.inventario.buscar_por_variante_bloqueada.return_value = stock

        resultado = self.servicio.cancelar(pedido.id, CLIENTE)

        assert resultado.estado == EstadoPedido.CANCELADO
        stock.liberar.assert_called_once_with(4)
        self.inventario.guardar.assert_called_once_with(stock)
        self.escritor_pedido.guardar.assert_called_once_with(pedido)

    def test_cancelar_pedido_de_otro_cliente_no_modifica_nada(self) -> None:
        pedido = PedidoFactory.crear(
            "otro-cliente",
            "carrito-1",
            [DetallePedido("variante-a", 1, Dinero(Decimal(5)))],
        )
        self.lector_pedido.buscar_por_id_para_actualizar.return_value = pedido

        with pytest.raises(PedidoNoPerteneceAClienteError):
            self.servicio.cancelar(pedido.id, CLIENTE)

        assert pedido.estado == EstadoPedido.CREADO
        self.inventario.guardar.assert_not_called()
        self.escritor_pedido.guardar.assert_not_called()

    def test_cancelar_pedido_inexistente(self) -> None:
        self.lector_pedido.buscar_por_id_para_actualizar.return_value = None

        with pytest.raises(PedidoNoEncontradoError):
            self.servicio.cancelar("pedido-x")

        self.escritor_pedido.guardar.assert_not_called()
