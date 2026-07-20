"""Pruebas de integracion del repositorio Django de pagos."""

from decimal import Decimal

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.ventas.pagos.domain.pago import Pago, PagoFactory
from apps.ventas.pagos.infrastructure.repositories import DjangoRepositorioPago


pytestmark = pytest.mark.django_db


def crear_pago(pedido_id: str = "pedido-1") -> Pago:
    return PagoFactory.crear(
        pedido_id=pedido_id,
        monto=Dinero(Decimal("83.45"), "PEN"),
        metodo=MetodoPago.YAPE,
        referencia="yape-987",
    )


def test_guardar_y_recuperar_pago() -> None:
    repositorio = DjangoRepositorioPago()
    pago = crear_pago()

    repositorio.guardar(pago)
    recuperado = repositorio.buscar_por_id(pago.id)

    assert recuperado is not None
    assert recuperado.id == pago.id
    assert recuperado.pedido_id == "pedido-1"


def test_actualizar_estado() -> None:
    repositorio = DjangoRepositorioPago()
    pago = crear_pago()
    repositorio.guardar(pago)

    pago.aprobar()
    repositorio.guardar(pago)

    recuperado = repositorio.buscar_por_id(pago.id)
    assert recuperado is not None
    assert recuperado.estado == EstadoPago.APROBADO


def test_listar_por_pedido_solo_devuelve_coincidencias() -> None:
    repositorio = DjangoRepositorioPago()
    esperado = crear_pago("pedido-1")
    repositorio.guardar(esperado)
    repositorio.guardar(crear_pago("pedido-2"))

    pagos = repositorio.listar_por_pedido("pedido-1")

    assert [pago.id for pago in pagos] == [esperado.id]


def test_conversion_conserva_todos_los_datos() -> None:
    repositorio = DjangoRepositorioPago()
    pago = crear_pago()
    repositorio.guardar(pago)

    recuperado = repositorio.buscar_por_id(pago.id)

    assert recuperado is not None
    assert recuperado.monto.monto == Decimal("83.45")
    assert recuperado.monto.moneda == "PEN"
    assert recuperado.metodo == MetodoPago.YAPE
    assert recuperado.estado == EstadoPago.PENDIENTE
    assert recuperado.referencia == "yape-987"
    assert recuperado.fecha == pago.fecha


def test_listar_tiene_orden_determinista() -> None:
    repositorio = DjangoRepositorioPago()
    primero = crear_pago()
    segundo = crear_pago()
    repositorio.guardar(primero)
    repositorio.guardar(segundo)

    pagos = repositorio.listar()

    assert [pago.id for pago in pagos] == [primero.id, segundo.id]
