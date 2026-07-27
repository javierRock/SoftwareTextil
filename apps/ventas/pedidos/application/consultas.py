"""Casos de uso de lectura de pedidos.

Separado de `services.py` para que cada clase tenga una sola razon de cambio
(SRP) y para que el camino de lectura no dependa del contrato de escritura
(ISP).
"""

from apps.ventas.pedidos.domain.errors import PedidoNoEncontradoError
from apps.ventas.pedidos.domain.pedido import Pedido
from apps.ventas.pedidos.domain.repositorios import CatalogoPedidos, LectorPedido


class ConsultaPedidos:
    def __init__(self, lector: LectorPedido, catalogo: CatalogoPedidos) -> None:
        self._lector = lector
        self._catalogo = catalogo

    def obtener(self, pedido_id: str) -> Pedido:
        pedido = self._lector.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNoEncontradoError
        return pedido

    def listar(self, cliente_id: str | None = None) -> list[Pedido]:
        if cliente_id:
            return self._catalogo.listar_por_cliente(cliente_id)
        return self._catalogo.listar_todos()
