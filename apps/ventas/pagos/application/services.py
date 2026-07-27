"""Casos de uso del modulo de pagos."""

from contextlib import nullcontext
from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido, MetodoPago
from apps.ventas.pagos.application.ports import (
    FabricaUnidadTrabajo,
    PedidoParaPago,
    RepositorioPedidoPago,
)
from apps.ventas.pagos.domain.excepciones import (
    IdentificadorPagoInvalido,
    MontoNoCoincideConPedido,
    MontoPagoInvalido,
    PagoNoEncontrado,
    PagoPedidoDuplicado,
    PedidoNoAdmitePago,
    PedidoNoEncontrado,
    PedidoNoPerteneceCliente,
    PedidoPagoInvalido,
)
from apps.ventas.pagos.domain.pago import Pago, PagoFactory
from apps.ventas.pagos.domain.repositorios import PaginaPagos, RepositorioPago


class ServicioPagos:
    """Coordina pagos, pedidos y persistencia mediante abstracciones."""

    def __init__(
        self,
        repositorio_pago: RepositorioPago,
        repositorio_pedido: RepositorioPedidoPago,
        unidad_trabajo: FabricaUnidadTrabajo = nullcontext,
    ) -> None:
        self._pagos = repositorio_pago
        self._pedidos = repositorio_pedido
        self._unidad_trabajo = unidad_trabajo

    def registrar_pago(
        self,
        pedido_id: str,
        monto: Decimal,
        metodo: MetodoPago | str,
        cliente_id: str,
        referencia: str = "",
    ) -> Pago:
        if not isinstance(monto, Decimal) or monto <= 0:
            raise MontoPagoInvalido()
        pedido_id = self._normalizar_pedido_id(pedido_id)
        with self._unidad_trabajo():
            pedido = self._obtener_pedido(pedido_id, para_actualizar=True)
            self._validar_cliente(pedido, cliente_id)
            self._validar_pedido_creado(pedido)
            if pedido.total.monto != monto:
                raise MontoNoCoincideConPedido()
            if self._pagos.existe_por_pedido(pedido_id):
                raise PagoPedidoDuplicado()
            pago = PagoFactory.crear(
                pedido_id=pedido_id,
                monto=Dinero(monto, pedido.total.moneda),
                metodo=metodo,
                referencia=referencia,
            )
            self._pagos.crear(pago)
        return pago

    def obtener(self, pago_id: str, cliente_id: str | None = None) -> Pago:
        pago = self._obtener_existente(pago_id)
        if cliente_id is not None:
            self._validar_cliente(self._obtener_pedido(pago.pedido_id), cliente_id)
        return pago

    def listar(
        self,
        pagina: int,
        tamano_pagina: int,
        pedido_id: str | None = None,
        cliente_id: str | None = None,
    ) -> PaginaPagos:
        pedido_ids = self._obtener_pedidos_permitidos(pedido_id, cliente_id)
        return self._pagos.listar_pagina(
            limite=tamano_pagina,
            desplazamiento=(pagina - 1) * tamano_pagina,
            pedido_ids=pedido_ids,
        )

    def aprobar(self, pago_id: str) -> Pago:
        with self._unidad_trabajo():
            pago = self._obtener_existente(pago_id, para_actualizar=True)
            pago.aprobar()
            pedido = self._obtener_pedido(pago.pedido_id, para_actualizar=True)
            self._validar_pedido_creado(pedido)
            self._pagos.actualizar_estado(pago)
            self._pedidos.marcar_pagado(pedido.id)
        return pago

    def rechazar(self, pago_id: str) -> Pago:
        with self._unidad_trabajo():
            pago = self._obtener_existente(pago_id, para_actualizar=True)
            pago.rechazar()
            self._pagos.actualizar_estado(pago)
        return pago

    def _obtener_pedidos_permitidos(
        self,
        pedido_id: str | None,
        cliente_id: str | None,
    ) -> frozenset[str] | None:
        if pedido_id is not None:
            identificador = self._normalizar_pedido_id(pedido_id)
            pedido = self._obtener_pedido(identificador)
            if cliente_id is not None:
                self._validar_cliente(pedido, cliente_id)
            return frozenset({identificador})
        if cliente_id is not None:
            return self._pedidos.listar_ids_por_cliente(cliente_id)
        return None

    def _obtener_existente(
        self,
        pago_id: str,
        para_actualizar: bool = False,
    ) -> Pago:
        if not isinstance(pago_id, str) or not pago_id.strip():
            raise IdentificadorPagoInvalido()
        identificador = pago_id.strip()
        buscador = (
            self._pagos.buscar_por_id_para_actualizar
            if para_actualizar
            else self._pagos.buscar_por_id
        )
        pago = buscador(identificador)
        if pago is None:
            raise PagoNoEncontrado(identificador)
        return pago

    def _obtener_pedido(
        self,
        pedido_id: str,
        para_actualizar: bool = False,
    ) -> PedidoParaPago:
        buscador = (
            self._pedidos.buscar_por_id_para_actualizar
            if para_actualizar
            else self._pedidos.buscar_por_id
        )
        pedido = buscador(pedido_id)
        if pedido is None:
            raise PedidoNoEncontrado(pedido_id)
        return pedido

    @staticmethod
    def _validar_cliente(pedido: PedidoParaPago, cliente_id: str) -> None:
        if pedido.cliente_id != cliente_id:
            raise PedidoNoPerteneceCliente()

    @staticmethod
    def _validar_pedido_creado(pedido: PedidoParaPago) -> None:
        if pedido.estado != EstadoPedido.CREADO:
            raise PedidoNoAdmitePago()

    @staticmethod
    def _normalizar_pedido_id(pedido_id: str) -> str:
        if not isinstance(pedido_id, str) or not pedido_id.strip():
            raise PedidoPagoInvalido()
        return pedido_id.strip()
