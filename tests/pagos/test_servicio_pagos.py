"""Pruebas unitarias de los casos de uso de pagos."""

from contextlib import nullcontext
from dataclasses import replace
from decimal import Decimal

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, EstadoPedido, MetodoPago
from apps.ventas.pagos.application.ports import PedidoParaPago, RepositorioPedidoPago
from apps.ventas.pagos.application.services import ServicioPagos
from apps.ventas.pagos.domain.excepciones import (
    MontoNoCoincideConPedido,
    PagoPedidoDuplicado,
    PedidoNoAdmitePago,
    PedidoNoEncontrado,
    PedidoNoPerteneceCliente,
)
from apps.ventas.pagos.domain.pago import Pago
from apps.ventas.pagos.domain.repositorios import PaginaPagos, RepositorioPago


class RepositorioPagoMemoria(RepositorioPago):
    def __init__(self) -> None:
        self.pagos: dict[str, Pago] = {}
        self.creados = 0
        self.actualizados = 0

    def crear(self, pago: Pago) -> None:
        if self.existe_por_pedido(pago.pedido_id):
            raise PagoPedidoDuplicado()
        self.pagos[pago.id] = pago
        self.creados += 1

    def actualizar_estado(self, pago: Pago) -> None:
        self.pagos[pago.id] = pago
        self.actualizados += 1

    def buscar_por_id(self, pago_id: str) -> Pago | None:
        return self.pagos.get(pago_id)

    def buscar_por_id_para_actualizar(self, pago_id: str) -> Pago | None:
        return self.buscar_por_id(pago_id)

    def existe_por_pedido(self, pedido_id: str) -> bool:
        return any(pago.pedido_id == pedido_id for pago in self.pagos.values())

    def listar_pagina(
        self,
        limite: int,
        desplazamiento: int,
        pedido_ids: frozenset[str] | None = None,
    ) -> PaginaPagos:
        pagos = list(self.pagos.values())
        if pedido_ids is not None:
            pagos = [pago for pago in pagos if pago.pedido_id in pedido_ids]
        return PaginaPagos(pagos[desplazamiento : desplazamiento + limite], len(pagos))


class RepositorioPedidoMemoria(RepositorioPedidoPago):
    def __init__(self, pedidos: list[PedidoParaPago]) -> None:
        self.pedidos = {pedido.id: pedido for pedido in pedidos}

    def buscar_por_id(self, pedido_id: str) -> PedidoParaPago | None:
        return self.pedidos.get(pedido_id)

    def buscar_por_id_para_actualizar(
        self,
        pedido_id: str,
    ) -> PedidoParaPago | None:
        return self.buscar_por_id(pedido_id)

    def listar_ids_por_cliente(self, cliente_id: str) -> frozenset[str]:
        return frozenset(
            pedido.id
            for pedido in self.pedidos.values()
            if pedido.cliente_id == cliente_id
        )

    def marcar_pagado(self, pedido_id: str) -> None:
        pedido = self.pedidos[pedido_id]
        self.pedidos[pedido_id] = replace(pedido, estado=EstadoPedido.PAGADO)


@pytest.fixture
def repositorio_pago() -> RepositorioPagoMemoria:
    return RepositorioPagoMemoria()


@pytest.fixture
def repositorio_pedido() -> RepositorioPedidoMemoria:
    return RepositorioPedidoMemoria(
        [
            PedidoParaPago(
                id="pedido-1",
                cliente_id="cliente-1",
                total=Dinero(Decimal("40.00")),
                estado=EstadoPedido.CREADO,
            ),
            PedidoParaPago(
                id="pedido-2",
                cliente_id="cliente-2",
                total=Dinero(Decimal("40.00")),
                estado=EstadoPedido.CREADO,
            ),
        ]
    )


@pytest.fixture
def servicio(
    repositorio_pago: RepositorioPagoMemoria,
    repositorio_pedido: RepositorioPedidoMemoria,
) -> ServicioPagos:
    return ServicioPagos(repositorio_pago, repositorio_pedido, nullcontext)


def registrar(
    servicio: ServicioPagos,
    pedido_id: str = "pedido-1",
    cliente_id: str = "cliente-1",
) -> Pago:
    return servicio.registrar_pago(
        pedido_id=pedido_id,
        monto=Decimal("40.00"),
        metodo=MetodoPago.TRANSFERENCIA,
        referencia="transferencia-1",
        cliente_id=cliente_id,
    )


def test_registrar_pago_total_lo_guarda(
    servicio: ServicioPagos,
    repositorio_pago: RepositorioPagoMemoria,
) -> None:
    pago = registrar(servicio)

    assert repositorio_pago.buscar_por_id(pago.id) == pago
    assert repositorio_pago.creados == 1


def test_rechaza_pedido_inexistente(servicio: ServicioPagos) -> None:
    with pytest.raises(PedidoNoEncontrado):
        registrar(servicio, "pedido-inexistente")


def test_rechaza_pedido_de_otro_cliente(servicio: ServicioPagos) -> None:
    with pytest.raises(PedidoNoPerteneceCliente):
        registrar(servicio, "pedido-2", "cliente-1")


def test_rechaza_monto_distinto_al_total(servicio: ServicioPagos) -> None:
    with pytest.raises(MontoNoCoincideConPedido):
        servicio.registrar_pago(
            pedido_id="pedido-1",
            monto=Decimal("39.99"),
            metodo=MetodoPago.EFECTIVO,
            cliente_id="cliente-1",
        )


def test_rechaza_segundo_pago_del_pedido(servicio: ServicioPagos) -> None:
    registrar(servicio)

    with pytest.raises(PagoPedidoDuplicado):
        registrar(servicio)


def test_aprobar_actualiza_pago_y_pedido(
    servicio: ServicioPagos,
    repositorio_pago: RepositorioPagoMemoria,
    repositorio_pedido: RepositorioPedidoMemoria,
) -> None:
    pago = registrar(servicio)

    resultado = servicio.aprobar(pago.id)

    assert resultado.estado == EstadoPago.APROBADO
    assert repositorio_pago.actualizados == 1
    assert repositorio_pedido.pedidos["pedido-1"].estado == EstadoPedido.PAGADO


def test_rechazar_no_actualiza_pedido(
    servicio: ServicioPagos,
    repositorio_pedido: RepositorioPedidoMemoria,
) -> None:
    pago = registrar(servicio)

    resultado = servicio.rechazar(pago.id)

    assert resultado.estado == EstadoPago.RECHAZADO
    assert repositorio_pedido.pedidos["pedido-1"].estado == EstadoPedido.CREADO


def test_no_aprueba_si_pedido_dejo_de_estar_creado(
    servicio: ServicioPagos,
    repositorio_pedido: RepositorioPedidoMemoria,
) -> None:
    pago = registrar(servicio)
    repositorio_pedido.pedidos["pedido-1"] = replace(
        repositorio_pedido.pedidos["pedido-1"],
        estado=EstadoPedido.CANCELADO,
    )

    with pytest.raises(PedidoNoAdmitePago):
        servicio.aprobar(pago.id)


def test_listar_solo_pagos_del_cliente(servicio: ServicioPagos) -> None:
    esperado = registrar(servicio)
    registrar(servicio, "pedido-2", "cliente-2")

    pagina = servicio.listar(1, 20, cliente_id="cliente-1")

    assert pagina.total == 1
    assert pagina.pagos == [esperado]
