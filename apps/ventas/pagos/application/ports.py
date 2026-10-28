"""Puertos requeridos para coordinar pagos con otros contextos."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import TypeAlias

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido


@dataclass(frozen=True)
class PedidoParaPago:
    """Vista minima de Pedido necesaria por los casos de uso de pagos."""

    id: str
    cliente_id: str
    total: Dinero
    estado: EstadoPedido


class RepositorioPedidoPago(ABC):
    """Puerto anticorrupcion entre los contextos de pagos y pedidos."""

    @abstractmethod
    def buscar_por_id(self, pedido_id: str) -> PedidoParaPago | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id_para_actualizar(
        self,
        pedido_id: str,
    ) -> PedidoParaPago | None:
        raise NotImplementedError

    @abstractmethod
    def listar_ids_por_cliente(self, cliente_id: str) -> frozenset[str]:
        raise NotImplementedError

    @abstractmethod
    def marcar_pagado(self, pedido_id: str) -> None:
        raise NotImplementedError


FabricaUnidadTrabajo: TypeAlias = Callable[[], AbstractContextManager[object]]
