"""Repositorios concretos con Django ORM para pedidos.

`DjangoRepositorioPedido` hereda el contrato completo `RepositorioPedido` y
respeta su comportamiento esperado (LSP): no agrega precondiciones ni cambia el
tipo de retorno, por lo que puede sustituirse por cualquier otra
implementacion (ver `memoria.py`) sin tocar los servicios.
"""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.pedidos.domain.pedido import DetallePedido, Pedido
from apps.ventas.pedidos.domain.repositorios import RepositorioPedido
from apps.ventas.pedidos.infrastructure.models import DetallePedidoModel, PedidoModel


def _pedido_from_model(model: PedidoModel) -> Pedido:
    detalles = [
        DetallePedido(
            id=str(d.id),
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


class DjangoRepositorioPedido(RepositorioPedido):
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
                id=detalle.id,
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

    def listar_todos(self) -> list[Pedido]:
        return [_pedido_from_model(m) for m in PedidoModel.objects.all()]
