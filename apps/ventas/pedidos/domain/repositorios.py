"""Contratos de persistencia para pedidos.

Los contratos estan segregados (ISP): cada colaborador declara solo el
subconjunto de operaciones que realmente usa. La infraestructura implementa
`RepositorioPedido`, que compone los tres roles.
"""

from abc import ABC, abstractmethod

from apps.ventas.pedidos.domain.pedido import Pedido


class LectorPedido(ABC):
    """Lectura de un pedido puntual."""

    @abstractmethod
    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        raise NotImplementedError


class CatalogoPedidos(ABC):
    """Consultas de coleccion sobre pedidos."""

    @abstractmethod
    def listar_por_cliente(self, cliente_id: str) -> list[Pedido]:
        raise NotImplementedError

    @abstractmethod
    def listar_todos(self) -> list[Pedido]:
        raise NotImplementedError


class EscritorPedido(ABC):
    """Escritura de pedidos."""

    @abstractmethod
    def guardar(self, pedido: Pedido) -> None:
        raise NotImplementedError


class RepositorioPedido(LectorPedido, CatalogoPedidos, EscritorPedido, ABC):
    """Contrato completo que implementan los adaptadores de persistencia."""
