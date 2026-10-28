"""Repositorio en memoria de pedidos.

Implementa el mismo contrato `RepositorioPedido` que el adaptador Django y
respeta su comportamiento observable, de modo que los casos de uso funcionan
igual con cualquiera de los dos (LSP). Se usa en pruebas y en ejecuciones
locales sin base de datos.
"""

from copy import deepcopy

from apps.ventas.pedidos.domain.pedido import Pedido
from apps.ventas.pedidos.domain.repositorios import RepositorioPedido


class MemoriaRepositorioPedido(RepositorioPedido):
    def __init__(self, pedidos: list[Pedido] | None = None) -> None:
        self._pedidos: dict[str, Pedido] = {}
        for pedido in pedidos or []:
            self.guardar(pedido)

    def guardar(self, pedido: Pedido) -> None:
        # Se copia al guardar y al leer para imitar el limite transaccional de
        # una base de datos: quien tiene el agregado no muta lo persistido.
        self._pedidos[pedido.id] = deepcopy(pedido)

    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        pedido = self._pedidos.get(pedido_id)
        return deepcopy(pedido) if pedido is not None else None

    def buscar_por_id_para_actualizar(self, pedido_id: str) -> Pedido | None:
        return self.buscar_por_id(pedido_id)

    def listar_por_cliente(self, cliente_id: str) -> list[Pedido]:
        return [
            deepcopy(pedido)
            for pedido in self._pedidos.values()
            if pedido.cliente_id == cliente_id
        ]

    def listar_todos(self) -> list[Pedido]:
        return [deepcopy(pedido) for pedido in self._pedidos.values()]
