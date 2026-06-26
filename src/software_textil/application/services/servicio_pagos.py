"""Casos de uso de pagos."""

from software_textil.application.dtos.comandos import ProcesarPagoDTO
from software_textil.application.errors import NotFoundError
from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import EstadoPago, MetodoPago
from software_textil.domain.pagos.pago import Pago, PagoFactory
from software_textil.domain.pagos.repositorios import RepositorioPago
from software_textil.domain.pedidos.repositorios import RepositorioPedido


class ServicioPagos:
    def __init__(self, pagos: RepositorioPago, pedidos: RepositorioPedido, unit_of_work: UnitOfWork | None = None) -> None:
        self.pagos = pagos
        self.pedidos = pedidos
        self.uow = unit_of_work or NoOpUnitOfWork()

    def procesar_pago(self, dto: ProcesarPagoDTO) -> Pago:
        with self.uow:
            pedido = self.pedidos.buscar_por_id(dto.pedido_id)
            if pedido is None:
                raise NotFoundError("El pedido no existe")
            if any(pago.estado == EstadoPago.APROBADO for pago in self.pagos.listar_por_pedido(pedido.id)):
                raise ValueError("El pedido ya tiene un pago aprobado")
            monto = Dinero(dto.monto, dto.moneda)
            if monto != pedido.total:
                raise ValueError("El monto del pago no coincide con el total del pedido")
            pago = PagoFactory.crear(pedido.id, monto, MetodoPago(dto.metodo), dto.referencia)
            pago.aprobar()
            pedido.marcar_pagado()
            self.pagos.guardar(pago)
            self.pedidos.guardar(pedido)
            self.uow.commit()
        return pago
