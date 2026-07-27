"""Agregado de inventario que fusiona Stock e Inventario de los diagramas UML.

El stock se lleva por variante (talla y color), no por prenda: es la unica
unidad con la que trabaja el almacen.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from apps.compartido.domain.enums import EstadoAlerta, TipoMovimiento

UBICACION_POR_DEFECTO = "almacen"
UNIDAD_POR_DEFECTO = "unidad"


def _ahora() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class Stock:
    cantidad: int
    unidad: str = UNIDAD_POR_DEFECTO

    def __post_init__(self) -> None:
        if self.cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")


@dataclass
class MovimientoInventario:
    id: str
    stock_id: str
    tipo: TipoMovimiento
    cantidad: int
    motivo: str
    registrado_por: str
    fecha: datetime = field(default_factory=_ahora)


@dataclass
class AlertaStock:
    id: str
    stock_id: str
    nivel_actual: int
    nivel_minimo: int
    estado: EstadoAlerta = EstadoAlerta.PENDIENTE
    fecha: datetime = field(default_factory=_ahora)

    def atender(self) -> None:
        self.estado = EstadoAlerta.ATENDIDA


@dataclass
class MermaDefecto:
    tipo: str
    cantidad: int
    descripcion: str
    fecha_registro: datetime = field(default_factory=_ahora)


@dataclass
class StockVariante:
    """Existencias de una variante concreta en una ubicacion."""

    id: str
    variante_id: str
    cantidad_actual: int
    nivel_minimo: int
    cantidad_reservada: int = 0
    ubicacion: str = UBICACION_POR_DEFECTO
    unidad: str = UNIDAD_POR_DEFECTO
    ultima_actualizacion: datetime = field(default_factory=_ahora)

    @property
    def cantidad_disponible(self) -> int:
        """Lo que se puede comprometer: el total menos lo ya reservado."""
        return self.cantidad_actual - self.cantidad_reservada

    def registrar_ingreso(
        self,
        cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        self._validar_cantidad(cantidad)
        self.cantidad_actual += cantidad
        self.ultima_actualizacion = _ahora()
        return self._crear_movimiento(
            TipoMovimiento.INGRESO, cantidad, motivo, usuario_id
        )

    def registrar_salida(
        self,
        cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        self._validar_cantidad(cantidad)
        if cantidad > self.cantidad_disponible:
            raise ValueError("No hay stock suficiente para la salida")
        self.cantidad_actual -= cantidad
        self.ultima_actualizacion = _ahora()
        return self._crear_movimiento(
            TipoMovimiento.SALIDA, cantidad, motivo, usuario_id
        )

    def ajustar(
        self,
        nueva_cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        if nueva_cantidad < 0:
            raise ValueError("La cantidad ajustada no puede ser negativa")
        if nueva_cantidad < self.cantidad_reservada:
            raise ValueError("El ajuste no puede dejar menos stock del reservado")
        diferencia = abs(nueva_cantidad - self.cantidad_actual)
        self.cantidad_actual = nueva_cantidad
        self.ultima_actualizacion = _ahora()
        return self._crear_movimiento(
            TipoMovimiento.AJUSTE, diferencia, motivo, usuario_id
        )

    def reservar(self, cantidad: int) -> None:
        """Compromete unidades para un pedido sin sacarlas del almacen."""
        self._validar_cantidad(cantidad)
        if cantidad > self.cantidad_disponible:
            raise ValueError("No hay stock disponible para reservar")
        self.cantidad_reservada += cantidad
        self.ultima_actualizacion = _ahora()

    def liberar(self, cantidad: int) -> None:
        """Devuelve al disponible unidades reservadas que ya no se usaran."""
        self._validar_cantidad(cantidad)
        if cantidad > self.cantidad_reservada:
            raise ValueError("No se puede liberar mas de lo reservado")
        self.cantidad_reservada -= cantidad
        self.ultima_actualizacion = _ahora()

    def esta_bajo_minimo(self) -> bool:
        return self.cantidad_actual < self.nivel_minimo

    def generar_alerta_si_corresponde(self) -> AlertaStock | None:
        if not self.esta_bajo_minimo():
            return None
        return AlertaStock(
            id=str(uuid4()),
            stock_id=self.id,
            nivel_actual=self.cantidad_actual,
            nivel_minimo=self.nivel_minimo,
        )

    def _crear_movimiento(
        self,
        tipo: TipoMovimiento,
        cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        return MovimientoInventario(
            id=str(uuid4()),
            stock_id=self.id,
            tipo=tipo,
            cantidad=cantidad,
            motivo=motivo,
            registrado_por=usuario_id,
        )

    @staticmethod
    def _validar_cantidad(cantidad: int) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")


class InventarioFabrica:
    @staticmethod
    def crear(
        variante_id: str,
        stock_inicial: int,
        stock_minimo: int,
        ubicacion: str = UBICACION_POR_DEFECTO,
    ) -> StockVariante:
        if stock_inicial < 0:
            raise ValueError("El stock inicial no puede ser negativo")
        if stock_minimo < 0:
            raise ValueError("El stock minimo no puede ser negativo")
        return StockVariante(
            id=str(uuid4()),
            variante_id=variante_id,
            cantidad_actual=stock_inicial,
            nivel_minimo=stock_minimo,
            ubicacion=ubicacion,
        )
