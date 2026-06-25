"""Casos de uso de pedidos."""

from software_textil.application.dtos.comandos import CrearPedidoDTO
from software_textil.application.errors import NotFoundError
from software_textil.domain.compras.repositorios import RepositorioCarrito
from software_textil.domain.pedidos.pedido import DetallePedido, Pedido, PedidoFactory
from software_textil.domain.pedidos.repositorios import RepositorioPedido


class ServicioPedidos:
    def __init__(self, pedidos: RepositorioPedido, carritos: RepositorioCarrito) -> None:
        self.pedidos = pedidos
        self.carritos = carritos

    def generar_desde_carrito(self, dto: CrearPedidoDTO) -> Pedido:
        carrito = self.carritos.buscar_por_id(dto.carrito_id)
        if carrito is None:
            raise NotFoundError("El carrito no existe")
        if carrito.cliente_id != dto.cliente_id:
            raise ValueError("El carrito no pertenece al cliente indicado")
        detalles = [DetallePedido(item.prenda_id, item.cantidad, item.precio_unitario) for item in carrito.items]
        pedido = PedidoFactory.crear(dto.cliente_id, carrito.id, detalles)
        carrito.marcar_convertido()
        self.pedidos.guardar(pedido)
        self.carritos.guardar(carrito)
        return pedido

    def obtener_pedido(self, pedido_id: str) -> Pedido:
        return self._obtener(pedido_id)

    def cancelar(self, pedido_id: str) -> Pedido:
        pedido = self._obtener(pedido_id)
        pedido.cancelar()
        self.pedidos.guardar(pedido)
        return pedido

    def _obtener(self, pedido_id: str) -> Pedido:
        pedido = self.pedidos.buscar_por_id(pedido_id)
        if pedido is None:
            raise NotFoundError("El pedido no existe")
        return pedido
