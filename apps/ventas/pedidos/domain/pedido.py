"""Agregado de pedido refinado desde StarUML."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.pedidos.domain.errors import (
    CantidadDetalleInvalidaError,
    PedidoCanceladoError,
    PedidoNoCancelableError,
    PedidoSinDetallesError,
    PedidoYaCanceladoError,
    PedidoYaPagadoError,
)


@dataclass
class DetallePedido:
    variante_id: str
    cantidad: int
    precio_unitario: Dinero
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise CantidadDetalleInvalidaError

    def subtotal(self) -> Dinero:
        monto = self.precio_unitario.monto * Decimal(self.cantidad)
        return Dinero(monto, self.precio_unitario.moneda)


@dataclass
class Pedido:
    id: str
    cliente_id: str
    carrito_id: str
    detalles: list[DetallePedido]
    total: Dinero
    estado: EstadoPedido = EstadoPedido.CREADO
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))

    def cancelar(self) -> None:
        if self.estado == EstadoPedido.PAGADO:
            raise PedidoNoCancelableError
        if self.estado == EstadoPedido.CANCELADO:
            raise PedidoYaCanceladoError
        self.estado = EstadoPedido.CANCELADO

    def marcar_pagado(self) -> None:
        if self.estado == EstadoPedido.PAGADO:
            raise PedidoYaPagadoError
        if self.estado == EstadoPedido.CANCELADO:
            raise PedidoCanceladoError
        self.estado = EstadoPedido.PAGADO


class PedidoFactory:
    @staticmethod
    def crear(
        cliente_id: str, carrito_id: str, detalles: list[DetallePedido]
    ) -> Pedido:
        if not detalles:
            raise PedidoSinDetallesError
        total = detalles[0].subtotal()
        for detalle in detalles[1:]:
            total = total.sumar(detalle.subtotal())
        return Pedido(
            id=str(uuid4()),
            cliente_id=cliente_id,
            carrito_id=carrito_id,
            detalles=detalles,
            total=total,
        )
