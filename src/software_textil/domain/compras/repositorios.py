"""Contratos de persistencia para compras."""

from abc import ABC, abstractmethod

from software_textil.domain.compras.carrito import CarritoCompras


class RepositorioCarrito(ABC):
    @abstractmethod
    def guardar(self, carrito: CarritoCompras) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, carrito_id: str) -> CarritoCompras | None:
        raise NotImplementedError

    @abstractmethod
    def listar_por_cliente(self, cliente_id: str) -> list[CarritoCompras]:
        raise NotImplementedError
