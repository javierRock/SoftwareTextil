"""Pruebas unitarias de los casos de uso con un repositorio en memoria."""

from decimal import Decimal

import pytest

from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.ventas.pagos.application.services import ServicioPagos
from apps.ventas.pagos.domain.excepciones import (
    MontoPagoInvalido,
    PagoNoEncontrado,
)
from apps.ventas.pagos.domain.pago import Pago
from apps.ventas.pagos.domain.repositorios import RepositorioPago


class RepositorioPagoMemoria(RepositorioPago):
    """Fake del puerto de persistencia para aislar los casos de uso."""

    def __init__(self) -> None:
        self.pagos: dict[str, Pago] = {}
        self.guardados = 0

    def guardar(self, pago: Pago) -> None:
        self.pagos[pago.id] = pago
        self.guardados += 1

    def buscar_por_id(self, pago_id: str) -> Pago | None:
        return self.pagos.get(pago_id)

    def listar(self) -> list[Pago]:
        return list(self.pagos.values())

    def listar_por_pedido(self, pedido_id: str) -> list[Pago]:
        return [pago for pago in self.pagos.values() if pago.pedido_id == pedido_id]


@pytest.fixture
def repositorio() -> RepositorioPagoMemoria:
    return RepositorioPagoMemoria()


@pytest.fixture
def servicio(repositorio: RepositorioPagoMemoria) -> ServicioPagos:
    return ServicioPagos(repositorio)


def registrar(
    servicio: ServicioPagos,
    pedido_id: str = "pedido-1",
) -> Pago:
    return servicio.registrar_pago(
        pedido_id=pedido_id,
        monto=Decimal("40.00"),
        metodo=MetodoPago.TRANSFERENCIA,
        referencia="transferencia-1",
    )


def test_registrar_pago_lo_guarda(
    servicio: ServicioPagos,
    repositorio: RepositorioPagoMemoria,
) -> None:
    pago = registrar(servicio)

    assert repositorio.buscar_por_id(pago.id) == pago
    assert repositorio.guardados == 1


def test_obtener_pago_existente(servicio: ServicioPagos) -> None:
    pago = registrar(servicio)

    assert servicio.obtener(pago.id) == pago


def test_obtener_pago_inexistente_falla(servicio: ServicioPagos) -> None:
    with pytest.raises(PagoNoEncontrado):
        servicio.obtener("pago-inexistente")


def test_listar_todos_los_pagos(servicio: ServicioPagos) -> None:
    registrar(servicio, "pedido-1")
    registrar(servicio, "pedido-2")

    assert len(servicio.listar()) == 2


def test_listar_por_pedido(servicio: ServicioPagos) -> None:
    esperado = registrar(servicio, "pedido-1")
    registrar(servicio, "pedido-2")

    assert servicio.listar_por_pedido("pedido-1") == [esperado]


def test_aprobar_y_persistir(
    servicio: ServicioPagos,
    repositorio: RepositorioPagoMemoria,
) -> None:
    pago = registrar(servicio)

    resultado = servicio.aprobar(pago.id)

    assert resultado.estado == EstadoPago.APROBADO
    assert repositorio.guardados == 2


def test_rechazar_y_persistir(
    servicio: ServicioPagos,
    repositorio: RepositorioPagoMemoria,
) -> None:
    pago = registrar(servicio)

    resultado = servicio.rechazar(pago.id)

    assert resultado.estado == EstadoPago.RECHAZADO
    assert repositorio.guardados == 2


@pytest.mark.parametrize("monto", [Decimal("0"), Decimal("-0.01")])
def test_rechaza_montos_no_positivos(
    servicio: ServicioPagos,
    monto: Decimal,
) -> None:
    with pytest.raises(MontoPagoInvalido):
        servicio.registrar_pago(
            pedido_id="pedido-1",
            monto=monto,
            metodo=MetodoPago.EFECTIVO,
        )
