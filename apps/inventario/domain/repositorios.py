"""Contratos de persistencia para inventario."""

from abc import ABC, abstractmethod

from apps.inventario.domain.consultas import CategoriaStockAgrupada
from apps.inventario.domain.stock_prenda import AlertaStock, MovimientoInventario, StockPrenda


class RepositorioInventario(ABC):
    @abstractmethod
    def guardar(self, stock: StockPrenda) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_prenda(self, prenda_id: str) -> StockPrenda | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_prenda_bloqueado(self, prenda_id: str) -> StockPrenda | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, stock_id: str) -> StockPrenda | None:
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[StockPrenda]:
        raise NotImplementedError

    @abstractmethod
    def listar_por_categoria(self, categoria_id: str | None = None) -> list[CategoriaStockAgrupada]:
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
