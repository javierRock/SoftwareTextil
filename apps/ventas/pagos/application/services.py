"""Casos de uso del modulo de pagos."""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import MetodoPago
from apps.ventas.pagos.domain.excepciones import (
    IdentificadorPagoInvalido,
    MontoPagoInvalido,
    PagoNoEncontrado,
    PedidoPagoInvalido,
)
from apps.ventas.pagos.domain.pago import Pago, PagoFactory
from apps.ventas.pagos.domain.repositorios import RepositorioPago


class ServicioPagos:
    """Coordina los casos de uso sin depender de Django ni de DRF."""

    def __init__(self, repositorio_pago: RepositorioPago) -> None:
        self._repositorio_pago = repositorio_pago

    def registrar_pago(
        self,
        pedido_id: str,
        monto: Decimal,
        metodo: MetodoPago | str,
        referencia: str = "",
    ) -> Pago:
        if not isinstance(monto, Decimal) or monto <= 0:
            raise MontoPagoInvalido()
        pago = PagoFactory.crear(
            pedido_id=pedido_id,
            monto=Dinero(monto),
            metodo=metodo,
            referencia=referencia,
        )
        self._repositorio_pago.guardar(pago)
        return pago

    def obtener(self, pago_id: str) -> Pago:
        return self._obtener_existente(pago_id)

    def listar(self) -> list[Pago]:
        return self._repositorio_pago.listar()

    def listar_por_pedido(self, pedido_id: str) -> list[Pago]:
        if not pedido_id or not pedido_id.strip():
            raise PedidoPagoInvalido()
        return self._repositorio_pago.listar_por_pedido(pedido_id.strip())

    def aprobar(self, pago_id: str) -> Pago:
        pago = self._obtener_existente(pago_id)
        pago.aprobar()
        self._repositorio_pago.guardar(pago)
        return pago

    def rechazar(self, pago_id: str) -> Pago:
        pago = self._obtener_existente(pago_id)
        pago.rechazar()
        self._repositorio_pago.guardar(pago)
        return pago

    def _obtener_existente(self, pago_id: str) -> Pago:
        if not pago_id or not pago_id.strip():
            raise IdentificadorPagoInvalido()
        identificador = pago_id.strip()
        pago = self._repositorio_pago.buscar_por_id(identificador)
        if pago is None:
            raise PagoNoEncontrado(identificador)
        return pago
