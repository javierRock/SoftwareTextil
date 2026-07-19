"""Servicios de aplicacion para pedidos."""

from apps.ventas.carrito.infrastructure.repositories import DjangoRepositorioCarrito
from apps.ventas.pedidos.domain.errors import (
    CarritoNoEncontrado,
    CarritoNoPerteneceACliente,
    PedidoNoEncontrado,
)
from apps.ventas.pedidos.domain.pedido import DetallePedido, PedidoFactory
from apps.ventas.pedidos.infrastructure.repositories import DjangoRepositorioPedido


class ServicioPedidos:
    def __init__(
        self,
        repo_pedido: DjangoRepositorioPedido,
        repo_carrito: DjangoRepositorioCarrito,
    ) -> None:
        self.repo_pedido = repo_pedido
        self.repo_carrito = repo_carrito

    def generar_desde_carrito(self, carrito_id: str, cliente_id: str):
        carrito = self.repo_carrito.buscar_por_id(carrito_id)
        if carrito is None:
            raise CarritoNoEncontrado
        if carrito.cliente_id != cliente_id:
            raise CarritoNoPerteneceACliente

        detalles = [
            DetallePedido(
                prenda_id=item.prenda_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
            )
            for item in carrito.items
        ]
        pedido = PedidoFactory.crear(cliente_id=cliente_id, carrito_id=carrito_id, detalles=detalles)
        self.repo_pedido.guardar(pedido)
        return pedido

    def obtener_pedido(self, pedido_id: str):
        pedido = self.repo_pedido.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNoEncontrado
        return pedido

    def listar_por_cliente(self, cliente_id: str):
        return self.repo_pedido.listar_por_cliente(cliente_id)

    def cancelar(self, pedido_id: str):
        pedido = self.repo_pedido.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNoEncontrado
        pedido.cancelar()
        self.repo_pedido.guardar(pedido)
        return pedido
