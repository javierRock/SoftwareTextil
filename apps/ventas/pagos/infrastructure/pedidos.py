"""Adaptador entre pagos y el contexto de pedidos."""

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.models import PedidoModel
from apps.ventas.pagos.application.ports import PedidoParaPago, RepositorioPedidoPago
from apps.ventas.pagos.domain.excepciones import PedidoNoAdmitePago


def pedido_para_pago_desde_modelo(modelo: PedidoModel) -> PedidoParaPago:
    return PedidoParaPago(
        id=str(modelo.id),
        cliente_id=modelo.cliente_id,
        total=Dinero(modelo.total_monto, modelo.total_moneda),
        estado=EstadoPedido(modelo.estado),
    )


class DjangoRepositorioPedidoPago(RepositorioPedidoPago):
    """Consulta y actualiza solo los datos de Pedido requeridos por Pagos."""

    def buscar_por_id(self, pedido_id: str) -> PedidoParaPago | None:
        modelo = PedidoModel.objects.filter(id=pedido_id).first()
        return pedido_para_pago_desde_modelo(modelo) if modelo else None

    def buscar_por_id_para_actualizar(
        self,
        pedido_id: str,
    ) -> PedidoParaPago | None:
        modelo = PedidoModel.objects.select_for_update().filter(id=pedido_id).first()
        return pedido_para_pago_desde_modelo(modelo) if modelo else None

    def listar_ids_por_cliente(self, cliente_id: str) -> frozenset[str]:
        identificadores = PedidoModel.objects.filter(cliente_id=cliente_id).values_list(
            "id",
            flat=True,
        )
        return frozenset(str(identificador) for identificador in identificadores)

    def marcar_pagado(self, pedido_id: str) -> None:
        actualizados = PedidoModel.objects.filter(
            id=pedido_id,
            estado=EstadoPedido.CREADO.value,
        ).update(estado=EstadoPedido.PAGADO.value)
        if actualizados != 1:
            raise PedidoNoAdmitePago()
