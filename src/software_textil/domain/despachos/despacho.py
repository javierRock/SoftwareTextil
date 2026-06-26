"""Agregado de despacho y guia de remision."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from software_textil.domain.compartido.enums import EstadoDespacho


@dataclass
class GuiaRemision:
    numero: str
    fecha_emision: datetime
    punto_partida: str
    punto_llegada: str


@dataclass
class Despacho:
    id: str
    cliente: str
    estado: EstadoDespacho = EstadoDespacho.PENDIENTE
    fecha: datetime = field(default_factory=datetime.utcnow)
    movimientos_ids: list[str] = field(default_factory=list)
    guia_remision: GuiaRemision | None = None

    def agregar_salida(self, movimiento_id: str) -> None:
        if self.estado in {EstadoDespacho.CONFIRMADO, EstadoDespacho.CANCELADO}:
            raise ValueError("No se puede modificar un despacho finalizado")
        self.movimientos_ids.append(movimiento_id)

    def preparar(self) -> None:
        if not self.movimientos_ids:
            raise ValueError("Un despacho debe tener salidas asociadas")
        self.estado = EstadoDespacho.PREPARADO

    def confirmar(self) -> None:
        if self.estado != EstadoDespacho.PREPARADO:
            raise ValueError("Solo un despacho preparado puede confirmarse")
        self.estado = EstadoDespacho.CONFIRMADO

    def cancelar(self) -> None:
        if self.estado == EstadoDespacho.CONFIRMADO:
            raise ValueError("No se puede cancelar un despacho confirmado")
        self.estado = EstadoDespacho.CANCELADO


class FabricaDespacho:
    @staticmethod
    def crear(cliente: str, movimientos_ids: list[str] | None = None) -> Despacho:
        return Despacho(id=str(uuid4()), cliente=cliente, movimientos_ids=movimientos_ids or [])
