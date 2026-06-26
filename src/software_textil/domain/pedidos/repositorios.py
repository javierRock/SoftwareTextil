"""Contratos de persistencia para pedidos."""

from abc import ABC, abstractmethod

from software_textil.domain.pedidos.pedido import Pedido


class RepositorioPedido(ABC):
    @abstractmethod
    def guardar(self, pedido: Pedido) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_cliente(self, cliente_id: str) -> list[Pedido]:
        raise NotImplementedError
