"""Contratos de persistencia para catalogo."""

from abc import ABC, abstractmethod

from apps.catalogo.domain.prenda import Categoria, Prenda, TipoProducto


class RepositorioPrenda(ABC):
    @abstractmethod
    def guardar(self, prenda: Prenda) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, prenda_id: str) -> Prenda | None:
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[Prenda]:
        raise NotImplementedError


class RepositorioCatalogo(ABC):
    @abstractmethod
    def guardar_categoria(self, categoria: Categoria) -> None:
        raise NotImplementedError

    @abstractmethod
    def guardar_tipo_producto(self, tipo_producto: TipoProducto) -> None:
        raise NotImplementedError

    @abstractmethod
    def listar_categorias(self) -> list[Categoria]:
        raise NotImplementedError

    @abstractmethod
    def listar_tipos(self) -> list[TipoProducto]:
        raise NotImplementedError

    @abstractmethod
    def buscar_tipo(self, tipo_producto_id: str) -> TipoProducto | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_categoria(self, categoria_id: str) -> Categoria | None:
        raise NotImplementedError
