"""Objeto de valor para importes monetarios."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Dinero:
    monto: Decimal
    moneda: str = "PEN"

    def __post_init__(self) -> None:
        if self.monto < Decimal("0"):
            raise ValueError("El monto no puede ser negativo")
        if not self.moneda:
            raise ValueError("La moneda es obligatoria")

    def sumar(self, otro: "Dinero") -> "Dinero":
        self._validar_moneda(otro)
        return Dinero(self.monto + otro.monto, self.moneda)

    def restar(self, otro: "Dinero") -> "Dinero":
        self._validar_moneda(otro)
        return Dinero(self.monto - otro.monto, self.moneda)

    def _validar_moneda(self, otro: "Dinero") -> None:
        if self.moneda != otro.moneda:
            raise ValueError("No se pueden operar montos con distinta moneda")
