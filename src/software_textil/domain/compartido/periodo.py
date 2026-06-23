"""Periodos usados por contabilidad y reportes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Periodo:
    mes: int
    anio: int

    def __post_init__(self) -> None:
        if self.mes < 1 or self.mes > 12:
            raise ValueError("El mes debe estar entre 1 y 12")
        if self.anio < 2000:
            raise ValueError("El anio debe ser valido")

    @property
    def codigo(self) -> str:
        return f"{self.anio:04d}-{self.mes:02d}"
