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


def crear_pago(pedido_id: str = "pedido-1") -> Pago:
    return PagoFactory.crear(
        pedido_id=pedido_id,
        monto=Dinero(Decimal("83.45"), "PEN"),
        metodo=MetodoPago.YAPE,
        referencia="yape-987",
    )


def test_crear_y_recuperar_pago() -> None:
    repositorio = DjangoRepositorioPago()
    pago = crear_pago()

    repositorio.crear(pago)
    recuperado = repositorio.buscar_por_id(pago.id)

    assert recuperado is not None
    assert recuperado.id == pago.id
    assert recuperado.fecha == pago.fecha


def test_actualizar_estado_no_sobrescribe_datos_inmutables() -> None:
    repositorio = DjangoRepositorioPago()
    pago = crear_pago()
    repositorio.crear(pago)
    pago.aprobar()
    pago.pedido_id = "pedido-alterado"

    repositorio.actualizar_estado(pago)

    recuperado = repositorio.buscar_por_id(pago.id)
    assert recuperado is not None
    assert recuperado.estado == EstadoPago.APROBADO
    assert recuperado.pedido_id == "pedido-1"


def test_impide_dos_pagos_para_el_mismo_pedido() -> None:
    repositorio = DjangoRepositorioPago()
    repositorio.crear(crear_pago())

    with pytest.raises(PagoPedidoDuplicado):
        repositorio.crear(crear_pago())


def test_listar_pagina_filtra_y_cuenta() -> None:
    repositorio = DjangoRepositorioPago()
    esperado = crear_pago("pedido-1")
    repositorio.crear(esperado)
    repositorio.crear(crear_pago("pedido-2"))

    pagina = repositorio.listar_pagina(10, 0, frozenset({"pedido-1"}))

    assert pagina.total == 1
    assert [pago.id for pago in pagina.pagos] == [esperado.id]


def test_listar_con_conjunto_vacio_no_expone_pagos() -> None:
    repositorio = DjangoRepositorioPago()
    repositorio.crear(crear_pago())

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
) -> None:
    datos = {
        "pedido_id": "pedido-invalido",
        "monto_monto": Decimal(10),
        "monto_moneda": "PEN",
        "metodo": "efectivo",
        "referencia": "",
        "estado": "pendiente",
    }
    datos.update(datos_invalidos)

    with pytest.raises(IntegrityError), transaction.atomic():
        PagoModel.objects.create(**datos)
