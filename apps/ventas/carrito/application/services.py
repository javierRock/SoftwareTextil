"""Servicios de aplicacion para carrito de compras."""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.ventas.carrito.domain.carrito import CarritoFactory
from apps.ventas.carrito.domain.errors import CarritoNoEncontrado
from apps.ventas.carrito.domain.repositorios import RepositorioCarrito


class ServicioCompras:
    def __init__(self, repo_carrito: RepositorioCarrito) -> None:
        self.repo_carrito = repo_carrito

    def crear_carrito(self, cliente_id: str):
        carrito = CarritoFactory.crear(cliente_id=cliente_id)
        self.repo_carrito.guardar(carrito)
        return carrito

    def agregar_item(self, carrito_id: str, prenda_id: str, cantidad: int, precio_monto: str, precio_moneda: str = "PEN"):
        carrito = self.repo_carrito.buscar_por_id(carrito_id)
        if carrito is None:
            raise CarritoNoEncontrado
        carrito.agregar_item(prenda_id, cantidad, Dinero(Decimal(precio_monto), precio_moneda))
        self.repo_carrito.guardar(carrito)
        return carrito

    def quitar_item(self, carrito_id: str, prenda_id: str):
        carrito = self.repo_carrito.buscar_por_id(carrito_id)
        if carrito is None:
            raise CarritoNoEncontrado
        carrito.quitar_item(prenda_id)
        self.repo_carrito.guardar(carrito)
        return carrito

    def obtener_carrito(self, carrito_id: str):
        carrito = self.repo_carrito.buscar_por_id(carrito_id)
        if carrito is None:
            raise CarritoNoEncontrado
        return carrito

    def listar_carritos_cliente(self, cliente_id: str):
        return self.repo_carrito.listar_por_cliente(cliente_id)
