"""Casos de uso de compras y carrito."""

from software_textil.application.dtos.comandos import ActualizarItemCarritoDTO, AgregarItemCarritoDTO, CrearCarritoDTO
from software_textil.application.errors import NotFoundError
from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compras.carrito import CarritoCompras, CarritoFactory
from software_textil.domain.compras.repositorios import RepositorioCarrito


class ServicioCompras:
    def __init__(self, carritos: RepositorioCarrito) -> None:
        self.carritos = carritos

    def crear_carrito(self, dto: CrearCarritoDTO) -> CarritoCompras:
        carrito = CarritoFactory.crear(dto.cliente_id)
        self.carritos.guardar(carrito)
        return carrito

    def obtener_carrito(self, carrito_id: str) -> CarritoCompras:
        return self._obtener(carrito_id)

    def agregar_item(self, dto: AgregarItemCarritoDTO) -> CarritoCompras:
        carrito = self._obtener(dto.carrito_id)
        carrito.agregar_item(dto.prenda_id, dto.cantidad, Dinero(dto.precio_unitario, dto.moneda))
        self.carritos.guardar(carrito)
        return carrito

    def actualizar_item(self, dto: ActualizarItemCarritoDTO) -> CarritoCompras:
        carrito = self._obtener(dto.carrito_id)
        carrito.actualizar_cantidad(dto.prenda_id, dto.cantidad)
        self.carritos.guardar(carrito)
        return carrito

    def quitar_item(self, carrito_id: str, prenda_id: str) -> CarritoCompras:
        carrito = self._obtener(carrito_id)
        carrito.quitar_item(prenda_id)
        self.carritos.guardar(carrito)
        return carrito

    def _obtener(self, carrito_id: str) -> CarritoCompras:
        carrito = self.carritos.buscar_por_id(carrito_id)
        if carrito is None:
            raise NotFoundError("El carrito no existe")
        return carrito
