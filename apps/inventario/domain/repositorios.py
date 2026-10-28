"""Contratos de persistencia para inventario."""

from abc import ABC, abstractmethod

from apps.inventario.domain.consultas import (
    CategoriaStockAgrupada,
    VarianteStockBajoMinimo,
)
from apps.inventario.domain.stock_prenda import (
    AlertaStock,
    MovimientoInventario,
    StockVariante,
)


class RepositorioInventario(ABC):
    @abstractmethod
    def guardar(self, stock: StockVariante) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_variante(self, variante_id: str) -> StockVariante | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_variante_bloqueada(self, variante_id: str) -> StockVariante | None:
        """Lee el stock reservando la fila hasta el fin de la transaccion.

        Dos movimientos simultaneos sobre la misma variante leerian el mismo
        saldo y uno pisaria al otro. El bloqueo los serializa.
        """
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, stock_id: str) -> StockVariante | None:
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[StockVariante]:
        raise NotImplementedError

    @abstractmethod
    def listar_por_categoria(
        self,
        categoria_id: str | None = None,
    ) -> list[CategoriaStockAgrupada]:
        """Resumen de existencias: categoria, sus prendas y sus variantes."""
        raise NotImplementedError

    @abstractmethod
    def listar_bajo_minimo(self) -> list[VarianteStockBajoMinimo]:
        """Variantes cuyo stock cayo por debajo de su nivel minimo."""
        raise NotImplementedError


class RepositorioMovimientoInventario(ABC):
    @abstractmethod
    def guardar(self, movimiento: MovimientoInventario) -> None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_stock(self, stock_id: str) -> list[MovimientoInventario]:
        raise NotImplementedError


class RepositorioAlertaStock(ABC):
    @abstractmethod
    def guardar(self, alerta: AlertaStock) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_pendiente_por_stock(self, stock_id: str) -> AlertaStock | None:
        raise NotImplementedError
