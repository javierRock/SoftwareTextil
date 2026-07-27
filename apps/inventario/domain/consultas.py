"""Objetos de consulta para respuestas de inventario y reportes."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class PrendaStockAgrupada:
    prenda_id: str
    nombre: str
    cantidad: int


@dataclass(frozen=True)
class CategoriaStockAgrupada:
    categoria_id: str
    categoria: str
    cantidad_total: int
    prendas: list[PrendaStockAgrupada] = field(default_factory=list)


@dataclass(frozen=True)
class PrendaStockBajoMinimo:
    categoria_id: str
    categoria: str
    prenda_id: str
    prenda: str
    cantidad_actual: int
    nivel_minimo: int


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
        return sum((categoria.valorizacion_total for categoria in self.categorias), Decimal("0.00"))
