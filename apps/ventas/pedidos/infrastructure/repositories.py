"""Repositorios concretos con Django ORM para pedidos."""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.pedidos.domain.pedido import DetallePedido, Pedido
from apps.ventas.pedidos.infrastructure.models import DetallePedidoModel, PedidoModel


def _pedido_from_model(model: PedidoModel) -> Pedido:
    detalles = [
        DetallePedido(
            prenda_id=d.prenda_id,
            cantidad=d.cantidad,
            precio_unitario=Dinero(Decimal(d.precio_monto), d.precio_moneda),
        )
        for d in model.detalles.all()
    ]
    return Pedido(
        id=str(model.id),
        cliente_id=model.cliente_id,
        carrito_id=model.carrito_id,
        detalles=detalles,
        total=Dinero(Decimal(model.total_monto), model.total_moneda),
        estado=EstadoPedido(model.estado),
        fecha_creacion=model.fecha_creacion,
    )


class DjangoRepositorioPedido:
    def guardar(self, pedido: Pedido) -> None:
        model = PedidoModel.objects.filter(id=pedido.id).first()
        if model is None:
            model = PedidoModel(id=pedido.id)
        model.cliente_id = pedido.cliente_id
        model.carrito_id = pedido.carrito_id
        model.total_monto = pedido.total.monto
        model.total_moneda = pedido.total.moneda
        model.estado = pedido.estado.value
        model.save()

        model.detalles.all().delete()
        for detalle in pedido.detalles:
            DetallePedidoModel.objects.create(
                pedido=model,
                prenda_id=detalle.prenda_id,
                cantidad=detalle.cantidad,
                precio_monto=detalle.precio_unitario.monto,
                precio_moneda=detalle.precio_unitario.moneda,
            )

    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        model = PedidoModel.objects.filter(id=pedido_id).first()
        return _pedido_from_model(model) if model else None

    def listar_por_cliente(self, cliente_id: str) -> list[Pedido]:
        qs = PedidoModel.objects.filter(cliente_id=cliente_id)
        return [_pedido_from_model(m) for m in qs]
