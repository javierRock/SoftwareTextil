"""Casos de uso de escritura de pedidos.

Este servicio solo genera y cancela pedidos: las consultas viven en
`apps.ventas.pedidos.application.consultas` (SRP). Depende de contratos del
dominio, nunca de Django ni del ORM (DIP), y declara unicamente los roles de
lectura y escritura que usa, no los de catalogo (ISP).
"""

from apps.ventas.carrito.domain.carrito import CarritoCompras
from apps.ventas.carrito.domain.repositorios import EscritorCarrito, LectorCarrito
from apps.ventas.pedidos.domain.errors import (
    CarritoNoEncontradoError,
    CarritoNoPerteneceAClienteError,
    PedidoNoEncontradoError,
)
from apps.ventas.pedidos.domain.pedido import DetallePedido, Pedido, PedidoFactory
from apps.ventas.pedidos.domain.repositorios import EscritorPedido, LectorPedido


class ServicioPedidos:
    def __init__(
        self,
        lector_pedido: LectorPedido,
        escritor_pedido: EscritorPedido,
        lector_carrito: LectorCarrito,
        escritor_carrito: EscritorCarrito,
    ) -> None:
        self._lector_pedido = lector_pedido
        self._escritor_pedido = escritor_pedido
        self._lector_carrito = lector_carrito
        self._escritor_carrito = escritor_carrito

    def generar_desde_carrito(self, carrito_id: str, cliente_id: str) -> Pedido:
        carrito = self._obtener_carrito_del_cliente(carrito_id, cliente_id)
        detalles = self._construir_detalles(carrito)
        pedido = PedidoFactory.crear(
            cliente_id=cliente_id, carrito_id=carrito_id, detalles=detalles
        )
        # Cerrar el carrito antes de persistir: si ya fue convertido, esto falla aqui
        # y evita generar un pedido duplicado del mismo carrito.
        carrito.marcar_convertido()
        self._escritor_pedido.guardar(pedido)
        self._escritor_carrito.guardar(carrito)
        return pedido

    def cancelar(self, pedido_id: str) -> Pedido:
        pedido = self._lector_pedido.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNoEncontradoError
        pedido.cancelar()
        self._escritor_pedido.guardar(pedido)
        return pedido

    def _obtener_carrito_del_cliente(
        self, carrito_id: str, cliente_id: str
    ) -> CarritoCompras:
        carrito = self._lector_carrito.buscar_por_id(carrito_id)
        if carrito is None:
            raise CarritoNoEncontradoError
        if carrito.cliente_id != cliente_id:
            raise CarritoNoPerteneceAClienteError
        return carrito

    @staticmethod
    def _construir_detalles(carrito: CarritoCompras) -> list[DetallePedido]:
        return [
            DetallePedido(
                variante_id=item.variante_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
            )
            for item in carrito.items
        ]
