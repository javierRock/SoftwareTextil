"""Agregado de pedido refinado desde StarUML."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoPedido


@dataclass
class DetallePedido:
    prenda_id: str
    cantidad: int
    precio_unitario: Dinero

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise ValueError("La cantidad del detalle debe ser mayor a cero")

    def subtotal(self) -> Dinero:
        return Dinero(self.precio_unitario.monto * Decimal(self.cantidad), self.precio_unitario.moneda)


@dataclass
class Pedido:
    id: str
    cliente_id: str
    carrito_id: str
    detalles: list[DetallePedido]
    total: Dinero
    estado: EstadoPedido = EstadoPedido.CREADO
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)

    def cancelar(self) -> None:
        if self.estado == EstadoPedido.PAGADO:
            raise ValueError("No se puede cancelar un pedido pagado")
        self.estado = EstadoPedido.CANCELADO

    def marcar_pagado(self) -> None:
        if self.estado == EstadoPedido.CANCELADO:
            raise ValueError("No se puede pagar un pedido cancelado")
        self.estado = EstadoPedido.PAGADO


class PedidoFactory:
    @staticmethod
    def crear(cliente_id: str, carrito_id: str, detalles: list[DetallePedido]) -> Pedido:
        if not detalles:
            raise ValueError("Un pedido debe tener al menos un detalle")
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
