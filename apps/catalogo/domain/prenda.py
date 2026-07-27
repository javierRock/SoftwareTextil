"""Agregado de catalogo para prendas textiles."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from apps.catalogo.domain.excepciones import ValidacionError
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


@dataclass
class Categoria:
    id: str
    nombre: str
    descripcion: str = ""

    def __post_init__(self) -> None:
        self._asignar_datos(self.nombre, self.descripcion)

    def actualizar(self, nombre: str, descripcion: str) -> None:
        self._asignar_datos(nombre, descripcion)

    def _asignar_datos(self, nombre: str, descripcion: str) -> None:
        nombre_normalizado = nombre.strip() if isinstance(nombre, str) else ""
        if not nombre_normalizado:
            raise ValidacionError("El nombre de la categoria es obligatorio")
        if len(nombre_normalizado) > 120:
            raise ValidacionError("El nombre de la categoria no puede exceder 120 caracteres")
        if not isinstance(descripcion, str):
            raise ValidacionError("La descripcion de la categoria debe ser texto")
        self.nombre = nombre_normalizado
        self.descripcion = descripcion.strip()


@dataclass
class TipoProducto:
    id: str
    nombre: str
    atributos_base: dict[str, str] = field(default_factory=dict)
    activo: bool = True

    def __post_init__(self) -> None:
        self._asignar_datos(self.nombre, self.atributos_base)

    def actualizar(self, nombre: str, atributos_base: dict[str, str]) -> None:
        self._asignar_datos(nombre, atributos_base)

    def activar(self) -> None:
        self.activo = True

    def desactivar(self) -> None:
        self.activo = False

    def _asignar_datos(self, nombre: str, atributos_base: dict[str, str]) -> None:
        nombre_normalizado = nombre.strip() if isinstance(nombre, str) else ""
        if not nombre_normalizado:
            raise ValidacionError("El nombre del tipo de producto es obligatorio")
        if len(nombre_normalizado) > 120:
            raise ValidacionError("El nombre del tipo de producto no puede exceder 120 caracteres")
        if not isinstance(atributos_base, dict):
            raise ValidacionError("Los atributos base deben ser un objeto")
        if any(
            not isinstance(clave, str)
            or not clave.strip()
            or not isinstance(valor, str)
            for clave, valor in atributos_base.items()
        ):
            raise ValidacionError(
                "Los atributos base deben tener nombres no vacios y valores de texto"
            )
        self.nombre = nombre_normalizado
        self.atributos_base = dict(atributos_base)


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

    def __post_init__(self) -> None:
        nombre_normalizado = self.nombre.strip() if isinstance(self.nombre, str) else ""
        if not nombre_normalizado:
            raise ValidacionError("El nombre de la prenda es obligatorio")
        if len(nombre_normalizado) > 120:
            raise ValidacionError("El nombre de la prenda no puede exceder 120 caracteres")
        if not isinstance(self.descripcion, str):
            raise ValidacionError("La descripcion de la prenda debe ser texto")
        if not isinstance(self.precio, Dinero) or self.precio.monto <= 0:
            raise ValidacionError("El precio de la prenda debe ser mayor que cero")
        if (
            not isinstance(self.precio.moneda, str)
            or len(self.precio.moneda) != 3
            or not self.precio.moneda.isalpha()
            or not self.precio.moneda.isupper()
        ):
            raise ValidacionError("La moneda debe ser un codigo de tres letras mayusculas")
        if not isinstance(self.categoria_id, str) or not self.categoria_id.strip():
            raise ValidacionError("La categoria de la prenda es obligatoria")
        if self.tipo_producto_id is not None and (
            not isinstance(self.tipo_producto_id, str)
            or not self.tipo_producto_id.strip()
        ):
            raise ValidacionError("El tipo de producto de la prenda no es valido")
        self.nombre = nombre_normalizado
        self.descripcion = self.descripcion.strip()

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
