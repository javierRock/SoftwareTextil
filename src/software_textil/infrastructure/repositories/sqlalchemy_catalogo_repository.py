"""Repositorio SQLAlchemy para catalogo."""

import json
from decimal import Decimal

from software_textil.domain.catalogo.prenda import Categoria, Prenda, TipoProducto
from software_textil.domain.catalogo.repositorios import RepositorioCatalogo, RepositorioPrenda
from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoPrenda
from software_textil.infrastructure.persistence.database import db
from software_textil.infrastructure.persistence.models import CategoriaModel, PrendaModel, TipoProductoModel


class SQLAlchemyPrendaRepository(RepositorioPrenda):
    def guardar(self, prenda: Prenda) -> None:
        model = db.session.get(PrendaModel, prenda.id) or PrendaModel(id=prenda.id)
        model.nombre = prenda.nombre
        model.descripcion = prenda.descripcion
        model.precio_monto = prenda.precio.monto
        model.precio_moneda = prenda.precio.moneda
        model.categoria_id = prenda.categoria_id
        model.tipo_producto_id = prenda.tipo_producto_id
        model.estado = prenda.estado.value
        model.registrado_por = prenda.registrado_por
        model.fecha_registro = prenda.fecha_registro
        db.session.add(model)

    def buscar_por_id(self, prenda_id: str) -> Prenda | None:
        model = db.session.get(PrendaModel, prenda_id)
        return _prenda_from_model(model) if model else None

    def listar(self) -> list[Prenda]:
        return [_prenda_from_model(model) for model in PrendaModel.query.all()]


class SQLAlchemyCatalogoRepository(RepositorioCatalogo):
    def guardar_categoria(self, categoria: Categoria) -> None:
        db.session.merge(CategoriaModel(id=categoria.id, nombre=categoria.nombre, descripcion=categoria.descripcion))

    def guardar_tipo_producto(self, tipo_producto: TipoProducto) -> None:
        db.session.merge(
            TipoProductoModel(
                id=tipo_producto.id,
                nombre=tipo_producto.nombre,
                atributos_base=json.dumps(tipo_producto.atributos_base),
            )
        )


def _prenda_from_model(model: PrendaModel) -> Prenda:
    return Prenda(
        id=model.id,
        nombre=model.nombre,
        descripcion=model.descripcion,
        precio=Dinero(Decimal(model.precio_monto), model.precio_moneda),
        categoria_id=model.categoria_id,
        tipo_producto_id=model.tipo_producto_id,
        estado=EstadoPrenda(model.estado),
        registrado_por=model.registrado_por,
        fecha_registro=model.fecha_registro,
    )
