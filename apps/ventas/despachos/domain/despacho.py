"""Agregado de despacho: preparacion y entrega fisica de un pedido."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from apps.compartido.domain.enums import EstadoDespacho
from apps.ventas.despachos.domain.errors import (
    DespachoCanceladoError,
    DespachoConfirmadoError,
    DespachoNoPreparadoError,
    DireccionDespachoInvalidaError,
    GuiaRemisionInvalidaError,
)

LONGITUD_MAXIMA_DIRECCION = 250
LONGITUD_MAXIMA_SERIE = 10


def _ahora() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class GuiaRemision:
    """Documento que acompana el traslado fisico de las prendas."""

    serie: str
    numero: str
    transportista: str = ""
    fecha_emision: datetime = field(default_factory=_ahora)

    def __post_init__(self) -> None:
        if not self.serie.strip() or len(self.serie) > LONGITUD_MAXIMA_SERIE:
            raise GuiaRemisionInvalidaError
        if not self.numero.strip() or not self.numero.isdigit():
            raise GuiaRemisionInvalidaError

    @property
    def codigo(self) -> str:
        return f"{self.serie}-{self.numero}"


@dataclass
class Despacho:
    """Raiz del agregado: gobierna las transiciones y su guia de remision."""

    id: str
    pedido_id: str
    direccion_entrega: str
    estado: EstadoDespacho = EstadoDespacho.PENDIENTE
    responsable_id: str | None = None
    guia: GuiaRemision | None = None
    fecha_preparacion: datetime | None = None
    fecha_confirmacion: datetime | None = None

    def __post_init__(self) -> None:
        direccion = (
            self.direccion_entrega.strip()
            if isinstance(self.direccion_entrega, str)
            else ""
        )
        if not direccion or len(direccion) > LONGITUD_MAXIMA_DIRECCION:
            raise DireccionDespachoInvalidaError
        self.direccion_entrega = direccion

    def preparar(self, responsable_id: str) -> None:
        self._validar_modificable()
        self.estado = EstadoDespacho.PREPARADO
        self.responsable_id = responsable_id
        self.fecha_preparacion = _ahora()

    def confirmar(self, guia: GuiaRemision) -> None:
        """Solo se confirma lo que ya fue preparado y lleva guia."""
        self._validar_modificable()
        if self.estado != EstadoDespacho.PREPARADO:
            raise DespachoNoPreparadoError
        self.guia = guia
        self.estado = EstadoDespacho.CONFIRMADO
        self.fecha_confirmacion = _ahora()

    def cancelar(self) -> None:
        self._validar_modificable()
        self.estado = EstadoDespacho.CANCELADO

    def _validar_modificable(self) -> None:
        if self.estado == EstadoDespacho.CONFIRMADO:
            raise DespachoConfirmadoError
        if self.estado == EstadoDespacho.CANCELADO:
            raise DespachoCanceladoError


class DespachoFabrica:
    @staticmethod
    def crear(pedido_id: str, direccion_entrega: str) -> Despacho:
        return Despacho(
            id=str(uuid4()),
            pedido_id=pedido_id,
            direccion_entrega=direccion_entrega,
        )
