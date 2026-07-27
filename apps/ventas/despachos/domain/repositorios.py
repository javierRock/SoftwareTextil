"""Contratos de persistencia para despachos."""

from abc import ABC, abstractmethod

from apps.ventas.despachos.domain.despacho import Despacho


class RepositorioDespacho(ABC):
    @abstractmethod
    def guardar(self, despacho: Despacho) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, despacho_id: str) -> Despacho | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id_para_actualizar(
        self, despacho_id: str
    ) -> Despacho | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_pedido(self, pedido_id: str) -> Despacho | None:
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[Despacho]:
        raise NotImplementedError
