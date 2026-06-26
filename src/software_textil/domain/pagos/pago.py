"""Agregado de pago refinado desde StarUML."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoPago, MetodoPago


@dataclass
class Pago:
    id: str
    pedido_id: str
    monto: Dinero
    metodo: MetodoPago
    referencia: str = ""
    estado: EstadoPago = EstadoPago.PENDIENTE
    fecha: datetime = field(default_factory=datetime.utcnow)

    def aprobar(self) -> None:
        if self.estado != EstadoPago.PENDIENTE:
            raise ValueError("Solo se puede aprobar un pago pendiente")
        self.estado = EstadoPago.APROBADO

    def rechazar(self) -> None:
        if self.estado != EstadoPago.PENDIENTE:
            raise ValueError("Solo se puede rechazar un pago pendiente")
        self.estado = EstadoPago.RECHAZADO


class PagoFactory:
    @staticmethod
    def crear(pedido_id: str, monto: Dinero, metodo: MetodoPago, referencia: str = "") -> Pago:
        return Pago(id=str(uuid4()), pedido_id=pedido_id, monto=monto, metodo=metodo, referencia=referencia)
