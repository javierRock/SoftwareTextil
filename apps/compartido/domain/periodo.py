"""Periodos usados por contabilidad y reportes."""

from dataclasses import dataclass

PRIMER_MES = 1
ULTIMO_MES = 12
ANIO_MINIMO = 2000


@dataclass(frozen=True)
class Periodo:
    mes: int
    anio: int

    def __post_init__(self) -> None:
        if not PRIMER_MES <= self.mes <= ULTIMO_MES:
            raise ValueError("El mes debe estar entre 1 y 12")
        if self.anio < ANIO_MINIMO:
            raise ValueError("El anio debe ser valido")

    @property
    def codigo(self) -> str:
        return f"{self.anio:04d}-{self.mes:02d}"
