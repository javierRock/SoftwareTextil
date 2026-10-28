"""Repositorio en memoria del carrito de compras.

Implementa el mismo contrato `RepositorioCarrito` que el adaptador Django y
respeta su comportamiento observable, de modo que los casos de uso funcionan
igual con cualquiera de los dos (LSP). Se usa en pruebas y en ejecuciones
locales sin base de datos.
"""

from copy import deepcopy

from apps.ventas.carrito.domain.carrito import CarritoCompras
from apps.ventas.carrito.domain.repositorios import RepositorioCarrito


class MemoriaRepositorioCarrito(RepositorioCarrito):
    def __init__(self, carritos: list[CarritoCompras] | None = None) -> None:
        self._carritos: dict[str, CarritoCompras] = {}
        for carrito in carritos or []:
            self.guardar(carrito)

    def guardar(self, carrito: CarritoCompras) -> None:
        # Se copia al guardar y al leer para imitar el limite transaccional de
        # una base de datos: quien tiene el agregado no muta lo persistido.
        self._carritos[carrito.id] = deepcopy(carrito)

    def buscar_por_id(self, carrito_id: str) -> CarritoCompras | None:
        carrito = self._carritos.get(carrito_id)
        return deepcopy(carrito) if carrito is not None else None

    def buscar_por_id_para_actualizar(
        self, carrito_id: str
    ) -> CarritoCompras | None:
        return self.buscar_por_id(carrito_id)

    def listar_por_cliente(self, cliente_id: str) -> list[CarritoCompras]:
        return [
            deepcopy(carrito)
            for carrito in self._carritos.values()
            if carrito.cliente_id == cliente_id
        ]

    def listar_todos(self) -> list[CarritoCompras]:
        return [deepcopy(carrito) for carrito in self._carritos.values()]
