"""Servicios de aplicacion para catalogo."""

from decimal import Decimal, InvalidOperation
from uuid import uuid4

from apps.catalogo.domain.prenda import (
    Categoria,
    Prenda,
    PrendaFabrica,
    TipoProducto,
)
from apps.catalogo.domain.repositorios import RepositorioCatalogo, RepositorioPrenda
from apps.compartido.domain.dinero import Dinero


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
    ) -> Prenda:
        if self.repo_catalogo.buscar_categoria(categoria_id) is None:
            raise ValueError("La categoria no existe")
        if (
            tipo_producto_id is not None
            and self.repo_catalogo.buscar_tipo(tipo_producto_id) is None
        ):
            raise ValueError("El tipo de producto no existe")
        try:
            monto = Decimal(precio_monto)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("El precio de la prenda no es valido") from exc
        moneda = precio_moneda.strip().upper() if isinstance(precio_moneda, str) else precio_moneda

        prenda = PrendaFabrica.crear(
            nombre=nombre,
            descripcion=descripcion,
            precio=Dinero(monto, moneda),
            categoria_id=categoria_id,
            registrado_por=registrado_por,
            tipo_producto_id=tipo_producto_id,
        )
        self.repo_prenda.guardar(prenda)
        return prenda

    def listar_prendas(self) -> list[Prenda]:
        return self.repo_prenda.listar()

    def listar_catalogo(self) -> list[Prenda]:
        return self.repo_prenda.listar_visibles()

    def buscar_prenda(self, prenda_id: str) -> Prenda | None:
        return self.repo_prenda.buscar_por_id(prenda_id)

    def desactivar_prenda(self, prenda_id: str) -> None:
        prenda = self.repo_prenda.buscar_por_id(prenda_id)
        if prenda is None:
            raise ValueError("Prenda no encontrada")
        prenda.desactivar()
        self.repo_prenda.guardar(prenda)

    def crear_categoria(self, nombre: str, descripcion: str = "") -> Categoria:
        categoria = Categoria(id=str(uuid4()), nombre=nombre, descripcion=descripcion)
        self.repo_catalogo.guardar_categoria(categoria)
        return categoria

    def listar_categorias(self) -> list[Categoria]:
        return self.repo_catalogo.listar_categorias()

    def buscar_categoria(self, categoria_id: str) -> Categoria:
        categoria = self.repo_catalogo.buscar_categoria(categoria_id)
        if categoria is None:
            raise ValueError("Categoria no encontrada")
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
            raise ValueError("Tipo de producto no encontrado")
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
