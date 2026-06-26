"""Contratos de persistencia para pagos."""

from abc import ABC, abstractmethod

from software_textil.domain.pagos.pago import Pago


class RepositorioPago(ABC):
    @abstractmethod
    def guardar(self, pago: Pago) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, pago_id: str) -> Pago | None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_pedido(self, pedido_id: str) -> list[Pago]:
        raise NotImplementedError
