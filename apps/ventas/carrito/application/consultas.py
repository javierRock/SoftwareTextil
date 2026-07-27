"""Casos de uso de lectura del carrito de compras.

Separado de `services.py` para que cada clase tenga una sola razon de cambio
(SRP) y para que el camino de lectura no dependa del contrato de escritura
(ISP).
"""

from apps.ventas.carrito.domain.carrito import CarritoCompras
from apps.ventas.carrito.domain.errors import CarritoNoEncontradoError
from apps.ventas.carrito.domain.repositorios import CatalogoCarritos, LectorCarrito


class ConsultaCarritos:
    def __init__(self, lector: LectorCarrito, catalogo: CatalogoCarritos) -> None:
        self._lector = lector
        self._catalogo = catalogo

    def obtener(self, carrito_id: str) -> CarritoCompras:
        carrito = self._lector.buscar_por_id(carrito_id)
        if carrito is None:
            raise CarritoNoEncontradoError
        return carrito

    def listar(self, cliente_id: str | None = None) -> list[CarritoCompras]:
        if cliente_id:
            return self._catalogo.listar_por_cliente(cliente_id)
        return self._catalogo.listar_todos()
