"""Repositorios concretos con Django ORM para pagos."""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.ventas.pagos.domain.pago import Pago
from apps.ventas.pagos.infrastructure.models import PagoModel


def _pago_from_model(model: PagoModel) -> Pago:
    return Pago(
        id=str(model.id),
        pedido_id=model.pedido_id,
        monto=Dinero(Decimal(model.monto_monto), model.monto_moneda),
        metodo=MetodoPago(model.metodo),
        referencia=model.referencia,
        estado=EstadoPago(model.estado),
        fecha=model.fecha,
    )


class DjangoRepositorioPago:
    def guardar(self, pago: Pago) -> None:
        model = PagoModel.objects.filter(id=pago.id).first()
        if model is None:
            model = PagoModel(id=pago.id)
        model.pedido_id = pago.pedido_id
        model.monto_monto = pago.monto.monto
        model.monto_moneda = pago.monto.moneda
        model.metodo = pago.metodo.value
        model.referencia = pago.referencia
        model.estado = pago.estado.value
        model.save()

    def buscar_por_id(self, pago_id: str) -> Pago | None:
        model = PagoModel.objects.filter(id=pago_id).first()
        return _pago_from_model(model) if model else None

    def listar_por_pedido(self, pedido_id: str) -> list[Pago]:
        qs = PagoModel.objects.filter(pedido_id=pedido_id)
        return [_pago_from_model(m) for m in qs]
