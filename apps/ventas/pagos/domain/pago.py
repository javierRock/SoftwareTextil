"""Entidad, raiz de agregado y fabrica del dominio de pagos."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.ventas.pagos.domain.excepciones import (
    IdentificadorPagoInvalido,
    MetodoPagoNoSoportado,
    MontoPagoInvalido,
    PagoYaProcesado,
    PedidoPagoInvalido,
)
from apps.ventas.pagos.domain.politicas import ValidadorMetodoPago


@dataclass
class Pago:
    """Raiz del agregado que protege las invariantes y transiciones del pago."""

    id: str
    pedido_id: str
    monto: Dinero
    metodo: MetodoPago
    referencia: str = ""
    estado: EstadoPago = EstadoPago.PENDIENTE
    fecha: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validador_metodo: ValidadorMetodoPago = field(
        default_factory=ValidadorMetodoPago,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise IdentificadorPagoInvalido()
        if not self.pedido_id or not self.pedido_id.strip():
            raise PedidoPagoInvalido()
        if not isinstance(self.monto.monto, Decimal) or self.monto.monto <= 0:
            raise MontoPagoInvalido()
        self.id = self.id.strip()
        self.pedido_id = self.pedido_id.strip()
        self.referencia = self.validador_metodo.validar(
            self.metodo,
            self.referencia,
        )

    def aprobar(self) -> None:
        if self.estado != EstadoPago.PENDIENTE:
            raise PagoYaProcesado()
        self.estado = EstadoPago.APROBADO

    def rechazar(self) -> None:
        if self.estado != EstadoPago.PENDIENTE:
            raise PagoYaProcesado()
        self.estado = EstadoPago.RECHAZADO


class PagoFactory:
    """Construye pagos nuevos con identidad y estado inicial consistentes."""

    @staticmethod
    def crear(
        pedido_id: str,
        monto: Dinero,
        metodo: MetodoPago | str,
        referencia: str = "",
    ) -> Pago:
        try:
            metodo_pago = MetodoPago(metodo)
        except (TypeError, ValueError) as error:
            raise MetodoPagoNoSoportado(metodo) from error
        return Pago(
            id=str(uuid4()),
            pedido_id=pedido_id,
            monto=monto,
            metodo=metodo_pago,
            referencia=referencia,
        )
