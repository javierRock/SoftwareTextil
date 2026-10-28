"""Pruebas de integracion del repositorio Django de pagos."""

from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.ventas.pagos.domain.excepciones import PagoPedidoDuplicado
from apps.ventas.pagos.domain.pago import Pago, PagoFactory
from apps.ventas.pagos.infrastructure.models import PagoModel
from apps.ventas.pagos.infrastructure.repositories import DjangoRepositorioPago

pytestmark = pytest.mark.django_db


@pytest.fixture
def pedido_id(crear_pedido) -> str:
    return str(crear_pedido().id)


@pytest.fixture
def otro_pedido_id(crear_pedido) -> str:
    return str(crear_pedido().id)


def crear_pago(pedido_id: str) -> Pago:
    return PagoFactory.crear(
        pedido_id=pedido_id,
        monto=Dinero(Decimal("83.45"), "PEN"),
        metodo=MetodoPago.YAPE,
        referencia="yape-987",
    )


def test_crear_y_recuperar_pago(pedido_id: str) -> None:
    repositorio = DjangoRepositorioPago()
    pago = crear_pago(pedido_id)

    repositorio.crear(pago)
    recuperado = repositorio.buscar_por_id(pago.id)

    assert recuperado is not None
    assert recuperado.id == pago.id
    assert recuperado.fecha == pago.fecha


def test_actualizar_estado_no_sobrescribe_datos_inmutables(
    pedido_id: str,
    otro_pedido_id: str,
) -> None:
    repositorio = DjangoRepositorioPago()
    pago = crear_pago(pedido_id)
    repositorio.crear(pago)
    pago.aprobar()
    pago.pedido_id = otro_pedido_id

    repositorio.actualizar_estado(pago)

    recuperado = repositorio.buscar_por_id(pago.id)
    assert recuperado is not None
    assert recuperado.estado == EstadoPago.APROBADO
    assert recuperado.pedido_id == pedido_id


def test_impide_dos_pagos_para_el_mismo_pedido(pedido_id: str) -> None:
    repositorio = DjangoRepositorioPago()
    repositorio.crear(crear_pago(pedido_id))

    with pytest.raises(PagoPedidoDuplicado), transaction.atomic():
        repositorio.crear(crear_pago(pedido_id))


def test_listar_pagina_filtra_y_cuenta(
    pedido_id: str,
    otro_pedido_id: str,
) -> None:
    repositorio = DjangoRepositorioPago()
    esperado = crear_pago(pedido_id)
    repositorio.crear(esperado)
    repositorio.crear(crear_pago(otro_pedido_id))

    pagina = repositorio.listar_pagina(10, 0, frozenset({pedido_id}))

    assert pagina.total == 1
    assert [pago.id for pago in pagina.pagos] == [esperado.id]


def test_listar_con_conjunto_vacio_no_expone_pagos(pedido_id: str) -> None:
    repositorio = DjangoRepositorioPago()
    repositorio.crear(crear_pago(pedido_id))

    pagina = repositorio.listar_pagina(10, 0, frozenset())

    assert pagina.total == 0
    assert pagina.pagos == []


@pytest.mark.parametrize(
    "datos_invalidos",
    [
        {"monto_monto": Decimal(0)},
        {"estado": "desconocido"},
        {"metodo": "bitcoin"},
        {"metodo": "tarjeta", "referencia": ""},
    ],
)
def test_base_de_datos_rechaza_invariantes_invalidas(
    datos_invalidos: dict[str, object],
    pedido_id: str,
) -> None:
    datos = {
        "pedido_id": pedido_id,
        "monto_monto": Decimal(10),
        "monto_moneda": "PEN",
        "metodo": "efectivo",
        "referencia": "",
        "estado": "pendiente",
    }
    datos.update(datos_invalidos)

    with pytest.raises(IntegrityError), transaction.atomic():
        PagoModel.objects.create(**datos)
