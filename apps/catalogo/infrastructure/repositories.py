"""Repositorios concretos con Django ORM para catalogo."""

from decimal import Decimal

from apps.catalogo.domain.prenda import Categoria, Prenda, TipoProducto
from apps.catalogo.domain.repositorios import RepositorioCatalogo, RepositorioPrenda
from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel, TipoProductoModel
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


def _categoria_from_model(model: CategoriaModel) -> Categoria:
    return Categoria(id=str(model.id), nombre=model.nombre, descripcion=model.descripcion)


def _tipo_from_model(model: TipoProductoModel) -> TipoProducto:
    return TipoProducto(
        id=str(model.id),
        nombre=model.nombre,
        atributos_base=model.atributos_base or {},
        activo=model.activo,
    )


def _prenda_from_model(model: PrendaModel) -> Prenda:
    return Prenda(
        id=str(model.id),
        nombre=model.nombre,
        descripcion=model.descripcion,
        precio=Dinero(Decimal(model.precio_monto), model.precio_moneda),
        categoria_id=str(model.categoria_id),
        tipo_producto_id=str(model.tipo_producto_id) if model.tipo_producto_id else None,
        estado=EstadoPrenda(model.estado),
        registrado_por=model.registrado_por,
        fecha_registro=model.fecha_registro,
    )


class DjangoRepositorioPrenda(RepositorioPrenda):
    def guardar(self, prenda: Prenda) -> None:
        model = PrendaModel.objects.filter(id=prenda.id).first()
        if model is None:
            model = PrendaModel(id=prenda.id)
        model.nombre = prenda.nombre
        model.descripcion = prenda.descripcion
        model.precio_monto = prenda.precio.monto
        model.precio_moneda = prenda.precio.moneda
        model.categoria_id = prenda.categoria_id
        model.tipo_producto_id = prenda.tipo_producto_id
        model.estado = prenda.estado.value
        model.registrado_por = prenda.registrado_por
        model.save()

    def buscar_por_id(self, prenda_id: str) -> Prenda | None:
        model = PrendaModel.objects.filter(id=prenda_id).first()
        return _prenda_from_model(model) if model else None

    def listar(self) -> list[Prenda]:
        return [_prenda_from_model(m) for m in PrendaModel.objects.all()]


class DjangoRepositorioCatalogo(RepositorioCatalogo):
    def guardar_categoria(self, categoria: Categoria) -> None:
        model = CategoriaModel.objects.filter(id=categoria.id).first()
        if model is None:
            model = CategoriaModel(id=categoria.id)
        model.nombre = categoria.nombre
        model.descripcion = categoria.descripcion
        model.save()

    def guardar_tipo_producto(self, tipo_producto: TipoProducto) -> None:
        model = TipoProductoModel.objects.filter(id=tipo_producto.id).first()
        if model is None:
            model = TipoProductoModel(id=tipo_producto.id)
        model.nombre = tipo_producto.nombre
        model.atributos_base = tipo_producto.atributos_base
        model.activo = tipo_producto.activo
        model.save()

    def listar_categorias(self) -> list[Categoria]:
        return [_categoria_from_model(m) for m in CategoriaModel.objects.all()]

    def listar_tipos(self) -> list[TipoProducto]:
        return [_tipo_from_model(m) for m in TipoProductoModel.objects.all()]

    def buscar_tipo(self, tipo_producto_id: str) -> TipoProducto | None:
        model = TipoProductoModel.objects.filter(id=tipo_producto_id).first()
        return _tipo_from_model(model) if model else None

    def buscar_categoria(self, categoria_id: str) -> Categoria | None:
        model = CategoriaModel.objects.filter(id=categoria_id).first()
        return _categoria_from_model(model) if model else None
