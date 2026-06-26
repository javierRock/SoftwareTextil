"""Contratos de persistencia para reportes."""

from abc import ABC, abstractmethod

from software_textil.domain.reportes.reporte import Reporte


class RepositorioReporte(ABC):
    @abstractmethod
    def guardar(self, reporte: Reporte) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, reporte_id: str) -> Reporte | None:
        raise NotImplementedError
