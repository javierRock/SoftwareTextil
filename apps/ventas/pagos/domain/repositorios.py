"""Contratos de persistencia para pagos."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from apps.ventas.pagos.domain.pago import Pago


@dataclass(frozen=True)
class PaginaPagos:
    """Resultado paginado independiente del framework HTTP."""

    pagos: list[Pago]
    total: int


class RepositorioPago(ABC):
    """Puerto de persistencia requerido por los casos de uso de pagos."""

    @abstractmethod
    def crear(self, pago: Pago) -> None:
        """Persiste un pago nuevo."""
        raise NotImplementedError

    @abstractmethod
    def actualizar_estado(self, pago: Pago) -> None:
        """Persiste unicamente el estado de un pago existente."""
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, pago_id: str) -> Pago | None:
        """Busca un pago por su identificador."""
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id_para_actualizar(self, pago_id: str) -> Pago | None:
        """Obtiene y bloquea un pago durante una unidad de trabajo."""
        raise NotImplementedError

    @abstractmethod
    def existe_por_pedido(self, pedido_id: str) -> bool:
        """Comprueba si un pedido ya tiene un pago."""
        raise NotImplementedError

    @abstractmethod
    def listar_pagina(
        self,
        limite: int,
        desplazamiento: int,
        pedido_ids: frozenset[str] | None = None,
    ) -> PaginaPagos:
        """Lista una pagina; None no filtra y un conjunto vacio no devuelve pagos."""
        raise NotImplementedError
