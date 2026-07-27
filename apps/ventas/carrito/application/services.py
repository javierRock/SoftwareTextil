"""Casos de uso de escritura del carrito de compras.

Este servicio solo modifica carritos: las consultas viven en
`apps.ventas.carrito.application.consultas` (SRP). Depende de los contratos
`LectorCarrito` y `EscritorCarrito`, nunca de la implementacion concreta (DIP),
y no declara el rol de catalogo porque no lista carritos (ISP).
"""

from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.ventas.carrito.domain.carrito import CarritoCompras, CarritoFactory
from apps.ventas.carrito.domain.errors import (
    CarritoNoEncontradoError,
    CarritoNoPerteneceAClienteError,
)
from apps.ventas.carrito.domain.repositorios import EscritorCarrito, LectorCarrito


class ServicioCompras:
    def __init__(
        self,
        lector: LectorCarrito,
        escritor: EscritorCarrito,
        resolver_precio: Callable[[str, int], Dinero] | None = None,
        unidad_trabajo: Callable[[], AbstractContextManager] = nullcontext,
    ) -> None:
        self._lector = lector
        self._escritor = escritor
        self._resolver_precio = resolver_precio
        self._unidad_trabajo = unidad_trabajo

    def crear_carrito(self, cliente_id: str) -> CarritoCompras:
        with self._unidad_trabajo():
            carrito = CarritoFactory.crear(cliente_id=cliente_id)
            self._escritor.guardar(carrito)
        return carrito

    def agregar_item(
        self,
        carrito_id: str,
        variante_id: str,
        cantidad: int,
        precio_monto: str | Decimal | None = None,
        *,
        cliente_id: str | None = None,
    ) -> CarritoCompras:
        with self._unidad_trabajo():
            carrito = self._obtener_carrito(carrito_id, para_actualizar=True)
            self._validar_cliente(carrito, cliente_id)
            cantidad_total = cantidad + next(
                (
                    item.cantidad
                    for item in carrito.items
                    if item.variante_id == variante_id
                ),
                0,
            )
            if self._resolver_precio is not None:
                precio_unitario = self._resolver_precio(variante_id, cantidad_total)
            else:
                precio_unitario = Dinero(Decimal(precio_monto), "PEN")
            carrito.agregar_item(variante_id, cantidad, precio_unitario)
            self._escritor.guardar(carrito)
        return carrito

    def quitar_item(
        self,
        carrito_id: str,
        variante_id: str,
        cliente_id: str | None = None,
    ) -> CarritoCompras:
        with self._unidad_trabajo():
            carrito = self._obtener_carrito(carrito_id, para_actualizar=True)
            self._validar_cliente(carrito, cliente_id)
            carrito.quitar_item(variante_id)
            self._escritor.guardar(carrito)
        return carrito

    def _obtener_carrito(
        self, carrito_id: str, para_actualizar: bool = False
    ) -> CarritoCompras:
        buscador = (
            self._lector.buscar_por_id_para_actualizar
            if para_actualizar
            else self._lector.buscar_por_id
        )
        carrito = buscador(carrito_id)
        if carrito is None:
            raise CarritoNoEncontradoError
        return carrito

    @staticmethod
    def _validar_cliente(
        carrito: CarritoCompras, cliente_id: str | None
    ) -> None:
        if cliente_id is not None and carrito.cliente_id != cliente_id:
            raise CarritoNoPerteneceAClienteError
