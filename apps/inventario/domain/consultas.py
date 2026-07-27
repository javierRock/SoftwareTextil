"""Objetos de consulta para respuestas de inventario.

Como el stock vive en la variante y no en la prenda, el resumen tiene tres
niveles: la categoria agrupa prendas, y cada prenda detalla sus variantes con
el SKU y la talla. Asi la misma respuesta sirve para la vista comercial
(cuanto hay de esta prenda) y para la de almacen (cuanto queda de la talla M).
"""

from dataclasses import dataclass, field


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
