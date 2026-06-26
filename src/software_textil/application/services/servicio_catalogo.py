"""Casos de uso de catalogo."""

from uuid import uuid4

from software_textil.application.dtos.comandos import RegistrarPrendaDTO
from software_textil.application.errors import NotFoundError
from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.catalogo.prenda import Categoria, Prenda, PrendaFabrica, TipoProducto
from software_textil.domain.catalogo.repositorios import RepositorioCatalogo, RepositorioPrenda
from software_textil.domain.compartido.dinero import Dinero


class ServicioCatalogo:
    def __init__(
        self,
        prendas: RepositorioPrenda,
        catalogo: RepositorioCatalogo,
        unit_of_work: UnitOfWork | None = None,
    ) -> None:
        self.prendas = prendas
        self.catalogo = catalogo
        self.uow = unit_of_work or NoOpUnitOfWork()

    def registrar_prenda(self, dto: RegistrarPrendaDTO) -> Prenda:
        with self.uow:
            prenda = PrendaFabrica.crear(
                nombre=dto.nombre,
                descripcion=dto.descripcion,
                precio=Dinero(dto.precio, dto.moneda),
                categoria_id=dto.categoria_id,
                registrado_por=dto.registrado_por,
                tipo_producto_id=dto.tipo_producto_id,
            )
            self.prendas.guardar(prenda)
            self.uow.commit()
        return prenda

    def editar_prenda(self, prenda_id: str, nombre: str | None = None, descripcion: str | None = None) -> Prenda:
        prenda = self.prendas.buscar_por_id(prenda_id)
        if prenda is None:
            raise NotFoundError("La prenda no existe")
        with self.uow:
            if nombre is not None:
                prenda.nombre = nombre
            if descripcion is not None:
                prenda.descripcion = descripcion
            self.prendas.guardar(prenda)
            self.uow.commit()
        return prenda

    def crear_categoria(self, nombre: str, descripcion: str = "") -> Categoria:
        with self.uow:
            categoria = Categoria(id=str(uuid4()), nombre=nombre, descripcion=descripcion)
            self.catalogo.guardar_categoria(categoria)
            self.uow.commit()
        return categoria

    def crear_tipo_producto(self, nombre: str, atributos_base: dict[str, str] | None = None) -> TipoProducto:
        with self.uow:
            tipo_producto = TipoProducto(id=str(uuid4()), nombre=nombre, atributos_base=atributos_base or {})
            self.catalogo.guardar_tipo_producto(tipo_producto)
            self.uow.commit()
        return tipo_producto
