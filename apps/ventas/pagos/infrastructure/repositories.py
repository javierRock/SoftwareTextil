"""Adaptador de persistencia de pagos basado en Django ORM."""

from django.db import IntegrityError

from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.compartido.infrastructure.mapeo import a_dinero, de_dinero, uuid_valido
from apps.ventas.pagos.domain.excepciones import PagoPedidoDuplicado
from apps.ventas.pagos.domain.pago import Pago
from apps.ventas.pagos.domain.repositorios import PaginaPagos, RepositorioPago
from apps.ventas.pagos.infrastructure.models import PagoModel


def pago_desde_modelo(modelo: PagoModel) -> Pago:
    """Convierte un registro ORM en un agregado de dominio."""

    return Pago(
        id=str(modelo.id),
        pedido_id=str(modelo.pedido_id),
        monto=a_dinero(modelo.monto_monto, modelo.monto_moneda),
        metodo=MetodoPago(modelo.metodo),
        referencia=modelo.referencia,
        estado=EstadoPago(modelo.estado),
        fecha=modelo.fecha,
    )


class DjangoRepositorioPago(RepositorioPago):
    """Implementa el contrato de pagos encapsulando Django ORM."""

    def crear(self, pago: Pago) -> None:
        monto, moneda = de_dinero(pago.monto)
        try:
            modelo = PagoModel.objects.create(
                id=pago.id,
                pedido_id=pago.pedido_id,
                monto_monto=monto,
                monto_moneda=moneda,
                metodo=pago.metodo.value,
                referencia=pago.referencia,
                estado=pago.estado.value,
            )
        except IntegrityError as error:
            raise PagoPedidoDuplicado() from error
        pago.fecha = modelo.fecha

    def actualizar_estado(self, pago: Pago) -> None:
        PagoModel.objects.filter(id=pago.id).update(estado=pago.estado.value)

    def buscar_por_id(self, pago_id: str) -> Pago | None:
        if uuid_valido(pago_id) is None:
            return None
        modelo = PagoModel.objects.filter(id=pago_id).first()
        return pago_desde_modelo(modelo) if modelo is not None else None

    def buscar_por_id_para_actualizar(self, pago_id: str) -> Pago | None:
        if uuid_valido(pago_id) is None:
            return None
        modelo = PagoModel.objects.select_for_update().filter(id=pago_id).first()
        return pago_desde_modelo(modelo) if modelo is not None else None

    def existe_por_pedido(self, pedido_id: str) -> bool:
        if uuid_valido(pedido_id) is None:
            return False
        return PagoModel.objects.filter(pedido_id=pedido_id).exists()

    def listar_pagina(
        self,
        limite: int,
        desplazamiento: int,
        pedido_ids: frozenset[str] | None = None,
    ) -> PaginaPagos:
        modelos = PagoModel.objects.all()
        if pedido_ids is not None:
            if not pedido_ids:
                return PaginaPagos([], 0)
            modelos = modelos.filter(pedido_id__in=pedido_ids)
        modelos = modelos.order_by("fecha", "id")
        total = modelos.count()
        pagina = modelos[desplazamiento : desplazamiento + limite]
        return PaginaPagos(
            pagos=[pago_desde_modelo(modelo) for modelo in pagina],
            total=total,
        )
