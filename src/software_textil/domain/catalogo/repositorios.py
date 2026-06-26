"""Contratos de persistencia para catalogo."""

from abc import ABC, abstractmethod

from software_textil.domain.catalogo.prenda import Categoria, Prenda, TipoProducto


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
