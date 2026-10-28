"""Contratos de persistencia para catalogo."""

from abc import ABC, abstractmethod

from apps.catalogo.domain.prenda import (
    Categoria,
    Prenda,
    TipoProducto,
    VariantePrenda,
)
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


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

    @abstractmethod
    def listar_visibles(self) -> list[Prenda]:
        raise NotImplementedError

    @abstractmethod
    def buscar(
        self,
        texto: str | None,
        categoria_id: str | None,
        tipo_producto_id: str | None,
        estado: EstadoPrenda,
    ) -> list[Prenda]:
        raise NotImplementedError


class RepositorioVariante(ABC):
    """Acceso directo a las variantes, para inventario, carrito y pedidos.

    Esos contextos necesitan resolver una variante concreta sin cargar toda la
    prenda: es la unidad sobre la que operan.
    """

    @abstractmethod
    def buscar_por_id(self, variante_id: str) -> VariantePrenda | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_sku(self, sku: str) -> VariantePrenda | None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_prenda(self, prenda_id: str) -> list[VariantePrenda]:
        raise NotImplementedError

    @abstractmethod
    def precio_efectivo(self, variante_id: str) -> Dinero | None:
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
