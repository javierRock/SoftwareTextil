"""Contratos de persistencia del carrito de compras.

Los contratos estan segregados (ISP): cada colaborador declara solo el
subconjunto de operaciones que realmente usa. La infraestructura implementa
`RepositorioCarrito`, que compone los tres roles.
"""

from abc import ABC, abstractmethod

from apps.ventas.carrito.domain.carrito import CarritoCompras


class LectorCarrito(ABC):
    """Lectura de un carrito puntual."""

    @abstractmethod
    def buscar_por_id(self, carrito_id: str) -> CarritoCompras | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id_para_actualizar(
        self, carrito_id: str
    ) -> CarritoCompras | None:
        raise NotImplementedError


class CatalogoCarritos(ABC):
    """Consultas de coleccion sobre carritos."""

    @abstractmethod
    def listar_por_cliente(self, cliente_id: str) -> list[CarritoCompras]:
        raise NotImplementedError

    @abstractmethod
    def listar_todos(self) -> list[CarritoCompras]:
        raise NotImplementedError


class EscritorCarrito(ABC):
    """Escritura de carritos."""

    @abstractmethod
    def guardar(self, carrito: CarritoCompras) -> None:
        raise NotImplementedError


class RepositorioCarrito(LectorCarrito, CatalogoCarritos, EscritorCarrito, ABC):
    """Contrato completo que implementan los adaptadores de persistencia."""
