"""Agregado de inventario que fusiona Stock e Inventario de los diagramas UML."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from software_textil.domain.compartido.enums import EstadoAlerta, TipoMovimiento


@dataclass(frozen=True)
class Stock:
    cantidad: int
    unidad: str = "unidad"

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
    fecha: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AlertaStock:
    id: str
    stock_id: str
    nivel_actual: int
    nivel_minimo: int
    estado: EstadoAlerta = EstadoAlerta.PENDIENTE
    fecha: datetime = field(default_factory=datetime.utcnow)

    def atender(self) -> None:
        self.estado = EstadoAlerta.ATENDIDA


@dataclass
class MermaDefecto:
    tipo: str
    cantidad: int
    descripcion: str
    fecha_registro: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StockPrenda:
    id: str
    prenda_id: str
    cantidad_actual: int
    nivel_minimo: int
    ubicacion: str = "almacen"
    unidad: str = "unidad"
    ultima_actualizacion: datetime = field(default_factory=datetime.utcnow)

    def registrar_ingreso(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        self._validar_cantidad(cantidad)
        self.cantidad_actual += cantidad
        self.ultima_actualizacion = datetime.utcnow()
        return self._crear_movimiento(TipoMovimiento.INGRESO, cantidad, motivo, usuario_id)

    def registrar_salida(self, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        self._validar_cantidad(cantidad)
        if cantidad > self.cantidad_actual:
            raise ValueError("No hay stock suficiente para la salida")
        self.cantidad_actual -= cantidad
        self.ultima_actualizacion = datetime.utcnow()
        return self._crear_movimiento(TipoMovimiento.SALIDA, cantidad, motivo, usuario_id)

    def ajustar(self, nueva_cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        if nueva_cantidad < 0:
            raise ValueError("La cantidad ajustada no puede ser negativa")
        diferencia = abs(nueva_cantidad - self.cantidad_actual)
        self.cantidad_actual = nueva_cantidad
        self.ultima_actualizacion = datetime.utcnow()
        return self._crear_movimiento(TipoMovimiento.AJUSTE, diferencia, motivo, usuario_id)

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
    def crear(prenda_id: str, stock_inicial: int, stock_minimo: int, ubicacion: str) -> StockPrenda:
        if stock_inicial < 0:
            raise ValueError("El stock inicial no puede ser negativo")
        if stock_minimo < 0:
            raise ValueError("El stock minimo no puede ser negativo")
        return StockPrenda(
            id=str(uuid4()),
            prenda_id=prenda_id,
            cantidad_actual=stock_inicial,
            nivel_minimo=stock_minimo,
            ubicacion=ubicacion,
        )
