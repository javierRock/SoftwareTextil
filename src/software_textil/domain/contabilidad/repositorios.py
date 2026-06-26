"""Contratos para persistencia contable."""

from abc import ABC, abstractmethod
from datetime import datetime

from software_textil.domain.contabilidad.contabilidad import EgresoTextil, Ingreso, PeriodoContable


class RepositorioIngreso(ABC):
    @abstractmethod
    def guardar(self, ingreso: Ingreso) -> None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_fecha(self, desde: datetime, hasta: datetime) -> list[Ingreso]:
        raise NotImplementedError


class RepositorioEgreso(ABC):
    @abstractmethod
    def guardar(self, egreso: EgresoTextil) -> None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_fecha(self, desde: datetime, hasta: datetime) -> list[EgresoTextil]:
        raise NotImplementedError


class RepositorioPeriodoContable(ABC):
    @abstractmethod
    def guardar(self, periodo: PeriodoContable) -> None:
        raise NotImplementedError
