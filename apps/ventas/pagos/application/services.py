"""Servicios de aplicacion para pagos."""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import MetodoPago
from apps.ventas.pagos.domain.pago import PagoFactory
from apps.ventas.pagos.infrastructure.repositories import DjangoRepositorioPago


class ServicioPagos:
    def __init__(self, repo_pago: DjangoRepositorioPago) -> None:
        self.repo_pago = repo_pago

    def registrar_pago(self, pedido_id: str, monto: str, metodo: str, referencia: str = ""):
        pago = PagoFactory.crear(
            pedido_id=pedido_id,
            monto=Dinero(Decimal(monto)),
            metodo=MetodoPago(metodo),
            referencia=referencia,
        )
        self.repo_pago.guardar(pago)
        return pago

    def aprobar(self, pago_id: str):
        pago = self.repo_pago.buscar_por_id(pago_id)
        if pago is None:
            raise ValueError("Pago no encontrado")
        pago.aprobar()
        self.repo_pago.guardar(pago)
        return pago

    def rechazar(self, pago_id: str):
        pago = self.repo_pago.buscar_por_id(pago_id)
        if pago is None:
            raise ValueError("Pago no encontrado")
        pago.rechazar()
        self.repo_pago.guardar(pago)
        return pago

    def listar_por_pedido(self, pedido_id: str):
        return self.repo_pago.listar_por_pedido(pedido_id)

    def obtener(self, pago_id: str):
        pago = self.repo_pago.buscar_por_id(pago_id)
        if pago is None:
            raise ValueError("Pago no encontrado")
        return pago
