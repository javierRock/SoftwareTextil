"""Contratos de persistencia para pagos."""

from abc import ABC, abstractmethod

from apps.ventas.pagos.domain.pago import Pago


class RepositorioPago(ABC):
    """Puerto de persistencia requerido por los casos de uso de pagos."""

    @abstractmethod
    def guardar(self, pago: Pago) -> None:
        """Crea o actualiza un pago."""
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, pago_id: str) -> Pago | None:
        """Busca un pago por su identificador."""
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[Pago]:
        """Lista todos los pagos en orden determinista."""
        raise NotImplementedError

    @abstractmethod
    def listar_por_pedido(self, pedido_id: str) -> list[Pago]:
        """Lista los pagos asociados a un pedido."""
        raise NotImplementedError
