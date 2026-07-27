"""Repositorios concretos con Django ORM para pedidos.

`DjangoRepositorioPedido` hereda el contrato completo `RepositorioPedido` y
respeta su comportamiento esperado (LSP): no agrega precondiciones ni cambia el
tipo de retorno, por lo que puede sustituirse por cualquier otra
implementacion (ver `memoria.py`) sin tocar los servicios.
"""

from apps.compartido.domain.enums import EstadoPedido
from apps.compartido.infrastructure.mapeo import a_dinero, de_dinero, uuid_valido
from apps.ventas.pedidos.domain.pedido import DetallePedido, Pedido
from apps.ventas.pedidos.domain.repositorios import RepositorioPedido
from apps.ventas.pedidos.infrastructure.models import DetallePedidoModel, PedidoModel


def _pedido_from_model(model: PedidoModel) -> Pedido:
    detalles = [
        DetallePedido(
            id=str(d.id),
            variante_id=str(d.variante_id),
            cantidad=d.cantidad,
            precio_unitario=a_dinero(d.precio_monto, d.precio_moneda),
        )
        for d in model.detalles.all()
    ]
    return Pedido(
        id=str(model.id),
        cliente_id=str(model.cliente_id),
        carrito_id=str(model.carrito_id),
        detalles=detalles,
        total=a_dinero(model.total_monto, model.total_moneda),
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
        model.total_monto, model.total_moneda = de_dinero(pedido.total)
        model.estado = pedido.estado.value
        model.save()

        model.detalles.all().delete()
        for detalle in pedido.detalles:
            precio_monto, precio_moneda = de_dinero(detalle.precio_unitario)
            DetallePedidoModel.objects.create(
                id=detalle.id,
                pedido=model,
                variante_id=detalle.variante_id,
                cantidad=detalle.cantidad,
                precio_monto=precio_monto,
                precio_moneda=precio_moneda,
            )

    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        if uuid_valido(pedido_id) is None:
            return None
        model = self._consulta().filter(id=pedido_id).first()
        return _pedido_from_model(model) if model else None

    def listar_por_cliente(self, cliente_id: str) -> list[Pedido]:
        if uuid_valido(cliente_id) is None:
            return []
        qs = self._consulta().filter(cliente_id=cliente_id)
        return [_pedido_from_model(m) for m in qs]

    def listar_todos(self) -> list[Pedido]:
        return [_pedido_from_model(m) for m in self._consulta()]

    @staticmethod
    def _consulta():
        """Trae el pedido y todos sus detalles sin una consulta por linea."""
        return PedidoModel.objects.prefetch_related("detalles")
