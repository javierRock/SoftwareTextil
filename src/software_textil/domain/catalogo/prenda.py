"""Agregado de catalogo para prendas textiles."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoPrenda


@dataclass
class Categoria:
    id: str
    nombre: str
    descripcion: str = ""


@dataclass
class TipoProducto:
    id: str
    nombre: str
    atributos_base: dict[str, str] = field(default_factory=dict)


@dataclass
class Prenda:
    id: str
    nombre: str
    descripcion: str
    precio: Dinero
    categoria_id: str
    tipo_producto_id: str | None = None
    estado: EstadoPrenda = EstadoPrenda.ACTIVA
    registrado_por: str | None = None
    fecha_registro: datetime = field(default_factory=datetime.utcnow)

    def activar(self) -> None:
        self.estado = EstadoPrenda.ACTIVA

    def desactivar(self) -> None:
        self.estado = EstadoPrenda.INACTIVA

    def cambiar_precio(self, precio: Dinero) -> None:
        self.precio = precio


class PrendaFabrica:
    @staticmethod
    def crear(
        nombre: str,
        descripcion: str,
        precio: Dinero,
        categoria_id: str,
        registrado_por: str,
        tipo_producto_id: str | None = None,
    ) -> Prenda:
        return Prenda(
            id=str(uuid4()),
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria_id=categoria_id,
            tipo_producto_id=tipo_producto_id,
            registrado_por=registrado_por,
        )
