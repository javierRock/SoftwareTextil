"""Contratos de persistencia para despachos."""

from abc import ABC, abstractmethod

from software_textil.domain.despachos.despacho import Despacho


class RepositorioDespacho(ABC):
    @abstractmethod
    def guardar(self, despacho: Despacho) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, despacho_id: str) -> Despacho | None:
        raise NotImplementedError
