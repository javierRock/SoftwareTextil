"""Objetos de consulta para respuestas de inventario."""

from dataclasses import dataclass, field


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
