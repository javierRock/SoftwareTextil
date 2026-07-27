"""Casos de uso de escritura del carrito de compras.

Este servicio solo modifica carritos: las consultas viven en
`apps.ventas.carrito.application.consultas` (SRP). Depende de los contratos
`LectorCarrito` y `EscritorCarrito`, nunca de la implementacion concreta (DIP),
y no declara el rol de catalogo porque no lista carritos (ISP).
"""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.ventas.carrito.domain.carrito import CarritoCompras, CarritoFactory
from apps.ventas.carrito.domain.errors import CarritoNoEncontradoError
from apps.ventas.carrito.domain.repositorios import EscritorCarrito, LectorCarrito


class ServicioCompras:
    def __init__(self, lector: LectorCarrito, escritor: EscritorCarrito) -> None:
        self._lector = lector
        self._escritor = escritor

    def crear_carrito(self, cliente_id: str) -> CarritoCompras:
        carrito = CarritoFactory.crear(cliente_id=cliente_id)
        self._escritor.guardar(carrito)
        return carrito

    def agregar_item(
        self,
        carrito_id: str,
        variante_id: str,
        cantidad: int,
        precio_monto: str,
        precio_moneda: str = "PEN",
    ) -> CarritoCompras:
        carrito = self._obtener_carrito(carrito_id)
        precio_unitario = Dinero(Decimal(precio_monto), precio_moneda)
        carrito.agregar_item(variante_id, cantidad, precio_unitario)
        self._escritor.guardar(carrito)
        return carrito

    def quitar_item(self, carrito_id: str, variante_id: str) -> CarritoCompras:
        carrito = self._obtener_carrito(carrito_id)
        carrito.quitar_item(variante_id)
        self._escritor.guardar(carrito)
        return carrito

    def _obtener_carrito(self, carrito_id: str) -> CarritoCompras:
        carrito = self._lector.buscar_por_id(carrito_id)
        if carrito is None:
            raise CarritoNoEncontradoError
        return carrito
