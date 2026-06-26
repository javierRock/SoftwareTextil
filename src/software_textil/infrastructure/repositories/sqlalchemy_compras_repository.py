"""Repositorio SQLAlchemy para compras y carrito."""

from decimal import Decimal

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoCarrito
from software_textil.domain.compras.carrito import CarritoCompras, ItemCarrito
from software_textil.domain.compras.repositorios import RepositorioCarrito
from software_textil.infrastructure.persistence.database import db
from software_textil.infrastructure.persistence.models import CarritoModel, ItemCarritoModel


class SQLAlchemyCarritoRepository(RepositorioCarrito):
    def guardar(self, carrito: CarritoCompras) -> None:
        model = db.session.get(CarritoModel, carrito.id) or CarritoModel(id=carrito.id)
        model.cliente_id = carrito.cliente_id
        model.estado = carrito.estado.value
        items_actuales = {item.id: item for item in model.items}
        nuevos_items = []
        for item in carrito.items:
            item_model = items_actuales.get(item.id) or ItemCarritoModel(id=item.id, carrito_id=carrito.id)
            item_model.prenda_id = item.prenda_id
            item_model.cantidad = item.cantidad
            item_model.precio_monto = item.precio_unitario.monto
            item_model.precio_moneda = item.precio_unitario.moneda
            nuevos_items.append(item_model)
        model.items = nuevos_items
        db.session.add(model)

    def buscar_por_id(self, carrito_id: str) -> CarritoCompras | None:
        model = db.session.get(CarritoModel, carrito_id)
        return _carrito_from_model(model) if model else None

    def listar_por_cliente(self, cliente_id: str) -> list[CarritoCompras]:
        models = CarritoModel.query.filter_by(cliente_id=cliente_id).all()
        return [_carrito_from_model(model) for model in models]


def _carrito_from_model(model: CarritoModel) -> CarritoCompras:
    return CarritoCompras(
        id=model.id,
        cliente_id=model.cliente_id,
        estado=EstadoCarrito(model.estado),
        items=[
            ItemCarrito(
                id=item.id,
                prenda_id=item.prenda_id,
                cantidad=item.cantidad,
                precio_unitario=Dinero(Decimal(item.precio_monto), item.precio_moneda),
            )
            for item in model.items
        ],
    )
