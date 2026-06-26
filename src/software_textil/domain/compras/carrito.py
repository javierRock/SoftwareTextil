"""Agregado de carrito de compras refinado desde StarUML."""

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import uuid4

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoCarrito


@dataclass
class ItemCarrito:
    id: str
    prenda_id: str
    cantidad: int
    precio_unitario: Dinero

    def __post_init__(self) -> None:
        if self.cantidad <= 0:
            raise ValueError("La cantidad del item debe ser mayor a cero")

    def subtotal(self) -> Dinero:
        return Dinero(self.precio_unitario.monto * Decimal(self.cantidad), self.precio_unitario.moneda)


@dataclass
class CarritoCompras:
    id: str
    cliente_id: str
    estado: EstadoCarrito = EstadoCarrito.ABIERTO
    items: list[ItemCarrito] = field(default_factory=list)

    def agregar_item(self, prenda_id: str, cantidad: int, precio_unitario: Dinero) -> None:
        self._validar_abierto()
        if cantidad <= 0:
            raise ValueError("La cantidad del item debe ser mayor a cero")
        existente = self._buscar_item(prenda_id)
        if existente is None:
            self.items.append(ItemCarrito(str(uuid4()), prenda_id, cantidad, precio_unitario))
            return
        if existente.precio_unitario.moneda != precio_unitario.moneda:
            raise ValueError("No se pueden mezclar monedas en el carrito")
        existente.cantidad += cantidad
        existente.precio_unitario = precio_unitario

    def actualizar_cantidad(self, prenda_id: str, cantidad: int) -> None:
        self._validar_abierto()
        if cantidad <= 0:
            self.quitar_item(prenda_id)
            return
        item = self._obtener_item(prenda_id)
        item.cantidad = cantidad

    def quitar_item(self, prenda_id: str) -> None:
        self._validar_abierto()
        item = self._obtener_item(prenda_id)
        self.items.remove(item)

    def total(self) -> Dinero:
        if not self.items:
            return Dinero(Decimal("0"))
        total = self.items[0].subtotal()
        for item in self.items[1:]:
            total = total.sumar(item.subtotal())
        return total

    def marcar_convertido(self) -> None:
        self._validar_abierto()
        if not self.items:
            raise ValueError("No se puede generar un pedido desde un carrito vacio")
        self.estado = EstadoCarrito.CONVERTIDO

    def cancelar(self) -> None:
        if self.estado == EstadoCarrito.CONVERTIDO:
            raise ValueError("No se puede cancelar un carrito convertido")
        self.estado = EstadoCarrito.CANCELADO

    def _validar_abierto(self) -> None:
        if self.estado != EstadoCarrito.ABIERTO:
            raise ValueError("El carrito no esta abierto")

    def _buscar_item(self, prenda_id: str) -> ItemCarrito | None:
        return next((item for item in self.items if item.prenda_id == prenda_id), None)

    def _obtener_item(self, prenda_id: str) -> ItemCarrito:
        item = self._buscar_item(prenda_id)
        if item is None:
            raise ValueError("El item no existe en el carrito")
        return item


class CarritoFactory:
    @staticmethod
    def crear(cliente_id: str) -> CarritoCompras:
        return CarritoCompras(id=str(uuid4()), cliente_id=cliente_id)
