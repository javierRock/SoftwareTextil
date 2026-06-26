"""Repositorio SQLAlchemy para pedidos."""

from decimal import Decimal
from uuid import uuid4

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoPedido
from software_textil.domain.pedidos.pedido import DetallePedido, Pedido
from software_textil.domain.pedidos.repositorios import RepositorioPedido
from software_textil.infrastructure.persistence.database import db
from software_textil.infrastructure.persistence.models import DetallePedidoModel, PedidoModel


class SQLAlchemyPedidoRepository(RepositorioPedido):
    def guardar(self, pedido: Pedido) -> None:
        model = db.session.get(PedidoModel, pedido.id) or PedidoModel(id=pedido.id)
        model.cliente_id = pedido.cliente_id
        model.carrito_id = pedido.carrito_id
        model.total_monto = pedido.total.monto
        model.total_moneda = pedido.total.moneda
        model.estado = pedido.estado.value
        model.fecha_creacion = pedido.fecha_creacion
        model.detalles = [
            DetallePedidoModel(
                id=str(uuid4()),
                pedido_id=pedido.id,
                prenda_id=detalle.prenda_id,
                cantidad=detalle.cantidad,
                precio_monto=detalle.precio_unitario.monto,
                precio_moneda=detalle.precio_unitario.moneda,
            )
            for detalle in pedido.detalles
        ]
        db.session.add(model)

    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        model = db.session.get(PedidoModel, pedido_id)
        return _pedido_from_model(model) if model else None

    def listar_por_cliente(self, cliente_id: str) -> list[Pedido]:
        models = PedidoModel.query.filter_by(cliente_id=cliente_id).all()
        return [_pedido_from_model(model) for model in models]


def _pedido_from_model(model: PedidoModel) -> Pedido:
    detalles = [
        DetallePedido(
            prenda_id=detalle.prenda_id,
            cantidad=detalle.cantidad,
            precio_unitario=Dinero(Decimal(detalle.precio_monto), detalle.precio_moneda),
        )
        for detalle in model.detalles
    ]
    return Pedido(
        id=model.id,
        cliente_id=model.cliente_id,
        carrito_id=model.carrito_id,
        detalles=detalles,
        total=Dinero(Decimal(model.total_monto), model.total_moneda),
        estado=EstadoPedido(model.estado),
        fecha_creacion=model.fecha_creacion,
    )
