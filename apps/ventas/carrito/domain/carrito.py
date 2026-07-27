"""Agregado de carrito de compras refinado desde StarUML."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoCarrito
from apps.ventas.carrito.domain.errors import (
    CantidadInvalidaError,
    CarritoCerradoError,
    CarritoConvertidoError,
    CarritoVacioError,
    ItemInexistenteError,
    MonedasIncompatiblesError,
)


@dataclass
class ItemCarrito:
    id: str
    variante_id: str
    cantidad: int
    precio_unitario: Dinero

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise CantidadInvalidaError

    def subtotal(self) -> Dinero:
        monto = self.precio_unitario.monto * Decimal(self.cantidad)
        return Dinero(monto, self.precio_unitario.moneda)


@dataclass
class CarritoCompras:
    id: str
    cliente_id: str
    estado: EstadoCarrito = EstadoCarrito.ABIERTO
    items: list[ItemCarrito] = field(default_factory=list)
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))

    def agregar_item(
        self, variante_id: str, cantidad: int, precio_unitario: Dinero
    ) -> None:
        self._validar_abierto()
        if cantidad <= 0:
            raise CantidadInvalidaError
        existente = self._buscar_item(variante_id)
        if existente is None:
            nuevo_item = ItemCarrito(
                str(uuid4()),
                variante_id,
                cantidad,
                precio_unitario,
            )
            self.items.append(nuevo_item)
            return
        if existente.precio_unitario.moneda != precio_unitario.moneda:
            raise MonedasIncompatiblesError
        existente.cantidad += cantidad
        existente.precio_unitario = precio_unitario

    def actualizar_cantidad(self, variante_id: str, cantidad: int) -> None:
        self._validar_abierto()
        if cantidad <= 0:
            self.quitar_item(variante_id)
            return
        item = self._obtener_item(variante_id)
        item.cantidad = cantidad

    def quitar_item(self, variante_id: str) -> None:
        self._validar_abierto()
        item = self._obtener_item(variante_id)
        self.items.remove(item)

    def total(self) -> Dinero:
        if not self.items:
            return Dinero(Decimal(0))
        total = self.items[0].subtotal()
        for item in self.items[1:]:
            total = total.sumar(item.subtotal())
        return total

    def marcar_convertido(self) -> None:
        self._validar_abierto()
        if not self.items:
            raise CarritoVacioError
        self.estado = EstadoCarrito.CONVERTIDO

    def cancelar(self) -> None:
        if self.estado == EstadoCarrito.CONVERTIDO:
            raise CarritoConvertidoError
        self.estado = EstadoCarrito.CANCELADO

    def _validar_abierto(self) -> None:
        if self.estado != EstadoCarrito.ABIERTO:
            raise CarritoCerradoError

    def _buscar_item(self, variante_id: str) -> ItemCarrito | None:
        return next(
            (item for item in self.items if item.variante_id == variante_id),
            None,
        )

    def _obtener_item(self, variante_id: str) -> ItemCarrito:
        item = self._buscar_item(variante_id)
        if item is None:
            raise ItemInexistenteError
        return item


class CarritoFactory:
    @staticmethod
    def crear(cliente_id: str) -> CarritoCompras:
        return CarritoCompras(id=str(uuid4()), cliente_id=cliente_id)
