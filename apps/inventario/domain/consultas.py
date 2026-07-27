"""Objetos de consulta para respuestas de inventario y reportes.

Como el stock vive en la variante y no en la prenda, el resumen tiene tres
niveles: la categoria agrupa prendas, y cada prenda detalla sus variantes con
el SKU y la talla. Asi la misma respuesta sirve para la vista comercial
(cuanto hay de esta prenda) y para la de almacen (cuanto queda de la talla M).
"""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class VarianteStockAgrupada:
    variante_id: str
    sku: str
    talla: str
    color: str
    cantidad: int
    cantidad_reservada: int = 0

    @property
    def cantidad_disponible(self) -> int:
        return self.cantidad - self.cantidad_reservada


@dataclass(frozen=True)
class PrendaStockAgrupada:
    """Total de la prenda y el desglose de las variantes que lo componen."""

    prenda_id: str
    nombre: str
    cantidad: int
    variantes: list[VarianteStockAgrupada] = field(default_factory=list)


@dataclass(frozen=True)
class CategoriaStockAgrupada:
    categoria_id: str
    categoria: str
    cantidad_total: int
    prendas: list[PrendaStockAgrupada] = field(default_factory=list)


@dataclass(frozen=True)
class VarianteStockBajoMinimo:
    """La reposicion se decide por variante: falta la talla M, no la camisa."""

    categoria_id: str
    categoria: str
    prenda_id: str
    prenda: str
    variante_id: str
    sku: str
    talla: str
    color: str
    cantidad_actual: int
    nivel_minimo: int

    @property
    def faltante(self) -> int:
        return max(self.nivel_minimo - self.cantidad_actual, 0)


@dataclass(frozen=True)
class ReporteInventarioPrenda:
    categoria_id: str
    categoria: str
    prenda_id: str
    prenda: str
    cantidad_actual: int
    precio_unitario: Decimal
    moneda: str

    @property
    def valorizacion(self) -> Decimal:
        return self.precio_unitario * Decimal(self.cantidad_actual)


@dataclass(frozen=True)
class ReporteInventarioCategoria:
    categoria_id: str
    categoria: str
    prendas: list[ReporteInventarioPrenda] = field(default_factory=list)

    @property
    def cantidad_total(self) -> int:
        return sum(prenda.cantidad_actual for prenda in self.prendas)

    @property
    def valorizacion_total(self) -> Decimal:
        return sum((prenda.valorizacion for prenda in self.prendas), Decimal("0.00"))


@dataclass(frozen=True)
class ReporteInventario:
    categorias: list[ReporteInventarioCategoria] = field(default_factory=list)

    @property
    def cantidad_total(self) -> int:
        return sum(categoria.cantidad_total for categoria in self.categorias)

    @property
    def valorizacion_total(self) -> Decimal:
        return sum(
            (categoria.valorizacion_total for categoria in self.categorias),
            Decimal("0.00"),
        )
