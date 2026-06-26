"""Repositorio SQLAlchemy para pagos."""

from decimal import Decimal

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoPago, MetodoPago
from software_textil.domain.pagos.pago import Pago
from software_textil.domain.pagos.repositorios import RepositorioPago
from software_textil.infrastructure.persistence.database import db
from software_textil.infrastructure.persistence.models import PagoModel


class SQLAlchemyPagoRepository(RepositorioPago):
    def guardar(self, pago: Pago) -> None:
        db.session.merge(
            PagoModel(
                id=pago.id,
                pedido_id=pago.pedido_id,
                monto_monto=pago.monto.monto,
                monto_moneda=pago.monto.moneda,
                metodo=pago.metodo.value,
                referencia=pago.referencia,
                estado=pago.estado.value,
                fecha=pago.fecha,
            )
        )

    def buscar_por_id(self, pago_id: str) -> Pago | None:
        model = db.session.get(PagoModel, pago_id)
        return _pago_from_model(model) if model else None

    def listar_por_pedido(self, pedido_id: str) -> list[Pago]:
        models = PagoModel.query.filter_by(pedido_id=pedido_id).all()
        return [_pago_from_model(model) for model in models]


def _pago_from_model(model: PagoModel) -> Pago:
    return Pago(
        id=model.id,
        pedido_id=model.pedido_id,
        monto=Dinero(Decimal(model.monto_monto), model.monto_moneda),
        metodo=MetodoPago(model.metodo),
        referencia=model.referencia,
        estado=EstadoPago(model.estado),
        fecha=model.fecha,
    )
