"""Agregado de catalogo para prendas textiles."""

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from apps.catalogo.domain.excepciones import ValidacionError
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda

LONGITUD_MAXIMA_NOMBRE = 120
LONGITUD_CODIGO_MONEDA = 3
LONGITUD_MAXIMA_TALLA = 20
LONGITUD_MAXIMA_COLOR = 40
LONGITUD_PREFIJO_SKU = 8
PATRON_TALLA = re.compile(r"[A-Z0-9-]+")
PATRON_COLOR = re.compile(r"[A-Z0-9 -]+")
TALLA_RESERVADA = "UNICA"


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
        if len(nombre_normalizado) > LONGITUD_MAXIMA_NOMBRE:
            raise ValidacionError(
                "El nombre de la categoria no puede exceder 120 caracteres"
            )
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
        if len(nombre_normalizado) > LONGITUD_MAXIMA_NOMBRE:
            raise ValidacionError(
                "El nombre del tipo de producto no puede exceder 120 caracteres"
            )
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
class VariantePrenda:
    """Unidad concreta que se vende y de la que se lleva stock (SKU).

    La prenda es el concepto comercial; la variante es la combinacion de talla
    y color que ocupa un lugar en el almacen. El inventario, los items del
    carrito y los detalles del pedido apuntan a la variante, porque es la unica
    forma de responder cuanto queda de la talla M en azul.
    """

    id: str
    prenda_id: str
    talla: str
    color: str = ""
    sku: str = ""
    precio: Dinero | None = None
    activa: bool = True

    def __post_init__(self) -> None:
        self.talla = self._normalizar_talla(self.talla)
        self.color = self._normalizar_color(self.color)
        if self.precio is not None and (
            not isinstance(self.precio, Dinero) or self.precio.monto <= 0
        ):
            raise ValidacionError("El precio de la variante debe ser mayor que cero")
        self.sku = self.sku.strip().upper() if isinstance(self.sku, str) else ""
        if not self.sku:
            self.sku = self.generar_sku(self.prenda_id, self.talla, self.color)

    def precio_efectivo(self, precio_prenda: Dinero) -> Dinero:
        """El precio propio de la variante, o el de la prenda si no lo define."""
        return self.precio or precio_prenda

    def activar(self) -> None:
        self.activa = True

    def desactivar(self) -> None:
        self.activa = False

    @staticmethod
    def generar_sku(prenda_id: str, talla: str, color: str) -> str:
        """Codigo estable y unico por combinacion de prenda, talla y color."""
        prefijo = prenda_id.replace("-", "")[:LONGITUD_PREFIJO_SKU].upper()
        partes = [prefijo, talla]
        if color:
            partes.append(color.replace(" ", ""))
        return "-".join(partes)

    @staticmethod
    def _normalizar_talla(talla: str) -> str:
        valor = talla.strip().upper() if isinstance(talla, str) else ""
        if (
            not valor
            or len(valor) > LONGITUD_MAXIMA_TALLA
            or PATRON_TALLA.fullmatch(valor) is None
            or valor == TALLA_RESERVADA
        ):
            raise ValidacionError("La talla de la prenda no es valida")
        return valor

    @staticmethod
    def _normalizar_color(color: str) -> str:
        if color is None:
            return ""
        if not isinstance(color, str):
            raise ValidacionError("El color de la variante debe ser texto")
        valor = color.strip().upper()
        if not valor:
            return ""
        if len(valor) > LONGITUD_MAXIMA_COLOR or PATRON_COLOR.fullmatch(valor) is None:
            raise ValidacionError("El color de la variante no es valido")
        return valor


@dataclass
class Prenda:
    """Raiz del agregado: la prenda gobierna el ciclo de vida de sus variantes."""

    id: str
    nombre: str
    descripcion: str
    precio: Dinero
    categoria_id: str
    tipo_producto_id: str | None = None
    variantes: list[VariantePrenda] = field(default_factory=list)
    estado: EstadoPrenda = EstadoPrenda.ACTIVA
    registrado_por: str | None = None
    fecha_registro: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        nombre_normalizado = self.nombre.strip() if isinstance(self.nombre, str) else ""
        if not nombre_normalizado:
            raise ValidacionError("El nombre de la prenda es obligatorio")
        if len(nombre_normalizado) > LONGITUD_MAXIMA_NOMBRE:
            raise ValidacionError(
                "El nombre de la prenda no puede exceder 120 caracteres"
            )
        if not isinstance(self.descripcion, str):
            raise ValidacionError("La descripcion de la prenda debe ser texto")
        if not isinstance(self.precio, Dinero) or self.precio.monto <= 0:
            raise ValidacionError("El precio de la prenda debe ser mayor que cero")
        if (
            not isinstance(self.precio.moneda, str)
            or len(self.precio.moneda) != LONGITUD_CODIGO_MONEDA
            or not self.precio.moneda.isalpha()
            or not self.precio.moneda.isupper()
        ):
            raise ValidacionError(
                "La moneda debe ser un codigo de tres letras mayusculas"
            )
        if not isinstance(self.categoria_id, str) or not self.categoria_id.strip():
            raise ValidacionError("La categoria de la prenda es obligatoria")
        if self.tipo_producto_id is not None and (
            not isinstance(self.tipo_producto_id, str)
            or not self.tipo_producto_id.strip()
        ):
            raise ValidacionError("El tipo de producto de la prenda no es valido")
        self.nombre = nombre_normalizado
        self.descripcion = self.descripcion.strip()
        self._validar_variantes(self.variantes)

    @property
    def tallas(self) -> list[str]:
        """Tallas disponibles, derivadas de las variantes del agregado."""
        return [variante.talla for variante in self.variantes]

    def definir_variantes(self, tallas: list[str], color: str = "") -> None:
        """Reemplaza las variantes por la combinacion de tallas y color dada."""
        if not isinstance(tallas, list):
            raise ValidacionError("Las tallas de la prenda deben ser una lista")
        variantes = [
            VariantePrenda(
                id=str(uuid4()),
                prenda_id=self.id,
                talla=talla,
                color=color,
            )
            for talla in tallas
        ]
        self._validar_variantes(variantes)
        self.variantes = variantes

    def agregar_variante(self, variante: VariantePrenda) -> None:
        self._validar_variantes([*self.variantes, variante])
        self.variantes.append(variante)

    def buscar_variante(self, variante_id: str) -> VariantePrenda | None:
        return next(
            (variante for variante in self.variantes if variante.id == variante_id),
            None,
        )

    def activar(self) -> None:
        self.estado = EstadoPrenda.ACTIVA

    def desactivar(self) -> None:
        self.estado = EstadoPrenda.INACTIVA

    def cambiar_precio(self, precio: Dinero) -> None:
        self.precio = precio

    def actualizar_datos_comerciales(
        self,
        nombre: str,
        descripcion: str,
        precio: Dinero,
        categoria_id: str,
        tipo_producto_id: str | None,
    ) -> None:
        candidata = Prenda(
            id=self.id,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria_id=categoria_id,
            tipo_producto_id=tipo_producto_id,
            variantes=self.variantes,
            estado=self.estado,
            registrado_por=self.registrado_por,
            fecha_registro=self.fecha_registro,
        )
        self.nombre = candidata.nombre
        self.descripcion = candidata.descripcion
        self.precio = candidata.precio
        self.categoria_id = candidata.categoria_id
        self.tipo_producto_id = candidata.tipo_producto_id

    @staticmethod
    def _validar_variantes(variantes: list[VariantePrenda]) -> None:
        if not isinstance(variantes, list):
            raise ValidacionError("Las variantes de la prenda deben ser una lista")
        combinaciones = [(variante.talla, variante.color) for variante in variantes]
        if len(combinaciones) != len(set(combinaciones)):
            raise ValidacionError("Las tallas de la prenda no pueden repetirse")


class VarianteFabrica:
    @staticmethod
    def crear(
        prenda_id: str,
        talla: str,
        color: str = "",
        precio: Dinero | None = None,
    ) -> VariantePrenda:
        return VariantePrenda(
            id=str(uuid4()),
            prenda_id=prenda_id,
            talla=talla,
            color=color,
            precio=precio,
        )


class PrendaFabrica:
    @staticmethod
    def crear(
        nombre: str,
        descripcion: str,
        precio: Dinero,
        categoria_id: str,
        registrado_por: str | None,
        tipo_producto_id: str | None = None,
        tallas: list[str] | None = None,
    ) -> Prenda:
        prenda = Prenda(
            id=str(uuid4()),
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria_id=categoria_id,
            tipo_producto_id=tipo_producto_id,
            registrado_por=registrado_por,
        )
        prenda.definir_variantes(tallas or [])
        return prenda
