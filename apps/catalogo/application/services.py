"""Servicios de aplicacion para catalogo."""

from decimal import Decimal, InvalidOperation
from uuid import uuid4

from apps.catalogo.domain.excepciones import (
    RecursoNoEncontradoError,
    ValidacionError,
)
from apps.catalogo.domain.prenda import (
    Categoria,
    Prenda,
    PrendaFabrica,
    TipoProducto,
)
from apps.catalogo.domain.repositorios import RepositorioCatalogo, RepositorioPrenda
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


class ServicioCatalogo:
    def __init__(
        self,
        repo_prenda: RepositorioPrenda,
        repo_catalogo: RepositorioCatalogo,
    ) -> None:
        self.repo_prenda = repo_prenda
        self.repo_catalogo = repo_catalogo

    def crear_prenda(
        self,
        nombre: str,
        descripcion: str,
        precio_monto: str,
        precio_moneda: str,
        categoria_id: str,
        registrado_por: str | None,
        tipo_producto_id: str | None = None,
        tallas: list[str] | None = None,
    ) -> Prenda:
        if self.repo_catalogo.buscar_categoria(categoria_id) is None:
            raise RecursoNoEncontradoError("La categoria no existe")
        if (
            tipo_producto_id is not None
            and self.repo_catalogo.buscar_tipo(tipo_producto_id) is None
        ):
            raise RecursoNoEncontradoError("El tipo de producto no existe")

        prenda = PrendaFabrica.crear(
            nombre=nombre,
            descripcion=descripcion,
            precio=self._crear_precio(precio_monto, precio_moneda),
            categoria_id=categoria_id,
            registrado_por=registrado_por,
            tipo_producto_id=tipo_producto_id,
            tallas=tallas,
        )
        self.repo_prenda.guardar(prenda)
        return prenda

    def listar_prendas(self) -> list[Prenda]:
        return self.repo_prenda.listar()

    def listar_catalogo(self) -> list[Prenda]:
        return self.repo_prenda.listar_visibles()

    def buscar_prendas(
        self,
        texto: str | None = None,
        categoria_id: str | None = None,
        tipo_producto_id: str | None = None,
        estado: str | None = None,
    ) -> list[Prenda]:
        texto = texto.strip() if texto else None
        categoria_id = categoria_id.strip() if categoria_id else None
        tipo_producto_id = tipo_producto_id.strip() if tipo_producto_id else None
        try:
            estado_prenda = EstadoPrenda(estado) if estado else EstadoPrenda.ACTIVA
        except ValueError as exc:
            raise ValidacionError("El estado de la prenda no es valido") from exc
        return self.repo_prenda.buscar(
            texto=texto,
            categoria_id=categoria_id,
            tipo_producto_id=tipo_producto_id,
            estado=estado_prenda,
        )

    def buscar_prenda(self, prenda_id: str) -> Prenda:
        prenda = self.repo_prenda.buscar_por_id(prenda_id)
        if prenda is None:
            raise RecursoNoEncontradoError("Prenda no encontrada")
        return prenda

    def actualizar_prenda(
        self,
        prenda_id: str,
        nombre: str,
        descripcion: str,
        precio_monto: str,
        precio_moneda: str,
        categoria_id: str,
        tipo_producto_id: str | None,
    ) -> Prenda:
        prenda = self.buscar_prenda(prenda_id)
        if self.repo_catalogo.buscar_categoria(categoria_id) is None:
            raise RecursoNoEncontradoError("La categoria no existe")
        if (
            tipo_producto_id is not None
            and self.repo_catalogo.buscar_tipo(tipo_producto_id) is None
        ):
            raise RecursoNoEncontradoError("El tipo de producto no existe")
        precio = self._crear_precio(precio_monto, precio_moneda)
        prenda.actualizar_datos_comerciales(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria_id=categoria_id,
            tipo_producto_id=tipo_producto_id,
        )
        self.repo_prenda.guardar(prenda)
        return prenda

    def activar_prenda(self, prenda_id: str) -> Prenda:
        prenda = self.buscar_prenda(prenda_id)
        prenda.activar()
        self.repo_prenda.guardar(prenda)
        return prenda

    def desactivar_prenda(self, prenda_id: str) -> Prenda:
        prenda = self.buscar_prenda(prenda_id)
        prenda.desactivar()
        self.repo_prenda.guardar(prenda)
        return prenda

    def crear_categoria(self, nombre: str, descripcion: str = "") -> Categoria:
        categoria = Categoria(id=str(uuid4()), nombre=nombre, descripcion=descripcion)
        self.repo_catalogo.guardar_categoria(categoria)
        return categoria

    def listar_categorias(self) -> list[Categoria]:
        return self.repo_catalogo.listar_categorias()

    def buscar_categoria(self, categoria_id: str) -> Categoria:
        categoria = self.repo_catalogo.buscar_categoria(categoria_id)
        if categoria is None:
            raise RecursoNoEncontradoError("Categoria no encontrada")
        return categoria

    def actualizar_categoria(
        self,
        categoria_id: str,
        nombre: str,
        descripcion: str,
    ) -> Categoria:
        categoria = self.buscar_categoria(categoria_id)
        categoria.actualizar(nombre, descripcion)
        self.repo_catalogo.guardar_categoria(categoria)
        return categoria

    def crear_tipo_producto(
        self,
        nombre: str,
        atributos_base: dict[str, str] | None = None,
    ) -> TipoProducto:
        tipo = TipoProducto(
            id=str(uuid4()),
            nombre=nombre,
            atributos_base={} if atributos_base is None else atributos_base,
        )
        self.repo_catalogo.guardar_tipo_producto(tipo)
        return tipo

    def listar_tipos(self) -> list[TipoProducto]:
        return self.repo_catalogo.listar_tipos()

    def buscar_tipo(self, tipo_producto_id: str) -> TipoProducto:
        tipo = self.repo_catalogo.buscar_tipo(tipo_producto_id)
        if tipo is None:
            raise RecursoNoEncontradoError("Tipo de producto no encontrado")
        return tipo

    def actualizar_tipo_producto(
        self,
        tipo_producto_id: str,
        nombre: str,
        atributos_base: dict[str, str],
    ) -> TipoProducto:
        tipo = self.buscar_tipo(tipo_producto_id)
        tipo.actualizar(nombre, atributos_base)
        self.repo_catalogo.guardar_tipo_producto(tipo)
        return tipo

    def activar_tipo_producto(self, tipo_producto_id: str) -> TipoProducto:
        tipo = self.buscar_tipo(tipo_producto_id)
        tipo.activar()
        self.repo_catalogo.guardar_tipo_producto(tipo)
        return tipo

    def desactivar_tipo_producto(self, tipo_producto_id: str) -> TipoProducto:
        tipo = self.buscar_tipo(tipo_producto_id)
        tipo.desactivar()
        self.repo_catalogo.guardar_tipo_producto(tipo)
        return tipo

    @staticmethod
    def _crear_precio(precio_monto: str, precio_moneda: str) -> Dinero:
        moneda = (
            precio_moneda.strip().upper()
            if isinstance(precio_moneda, str)
            else precio_moneda
        )
        try:
            return Dinero(Decimal(precio_monto), moneda)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValidacionError("El precio de la prenda no es valido") from exc
