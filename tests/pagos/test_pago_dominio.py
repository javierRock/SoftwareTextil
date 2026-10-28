"""Pruebas unitarias del agregado Pago."""

from decimal import Decimal

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.ventas.pagos.domain.excepciones import (
    IdentificadorPagoInvalido,
    LongitudDatoPagoInvalida,
    MetodoPagoNoSoportado,
    MontoPagoInvalido,
    PagoYaProcesado,
    PedidoPagoInvalido,
    ReferenciaPagoInvalida,
)
from apps.ventas.pagos.domain.pago import Pago, PagoFactory
from apps.ventas.pagos.domain.politicas import (
    PoliticaReferenciaPago,
    ReferenciaObligatoria,
    ValidadorMetodoPago,
)


class ReferenciaTransferenciaPersonalizada(PoliticaReferenciaPago):
    @property
    def metodos(self) -> frozenset[MetodoPago]:
        return frozenset({MetodoPago.TRANSFERENCIA})

    def validar(self, _metodo: MetodoPago, referencia: str) -> str:
        return f"EXT-{referencia.strip()}"


def crear_pago() -> Pago:
    return PagoFactory.crear(
        pedido_id="pedido-1",
        monto=Dinero(Decimal("25.50")),
        metodo=MetodoPago.TARJETA,
        referencia="operacion-123",
    )


def test_crear_pago_valido_inicia_pendiente() -> None:
    pago = crear_pago()

    assert pago.id
    assert pago.estado == EstadoPago.PENDIENTE
    assert pago.monto.monto == Decimal("25.50")


def test_aprobar_pago_pendiente() -> None:
    pago = crear_pago()

    pago.aprobar()

    assert pago.estado == EstadoPago.APROBADO


def test_rechazar_pago_pendiente() -> None:
    pago = crear_pago()

    pago.rechazar()

    assert pago.estado == EstadoPago.RECHAZADO


@pytest.mark.parametrize("transicion", ["aprobar", "rechazar"])
def test_no_repite_una_transicion_final(transicion: str) -> None:
    pago = crear_pago()
    getattr(pago, transicion)()

    with pytest.raises(PagoYaProcesado):
        getattr(pago, transicion)()


def test_no_cambia_de_aprobado_a_rechazado() -> None:
    pago = crear_pago()
    pago.aprobar()

    with pytest.raises(PagoYaProcesado):
        pago.rechazar()


def test_no_cambia_de_rechazado_a_aprobado() -> None:
    pago = crear_pago()
    pago.rechazar()

    with pytest.raises(PagoYaProcesado):
        pago.aprobar()


def test_rechaza_monto_cero() -> None:
    with pytest.raises(MontoPagoInvalido):
        PagoFactory.crear(
            pedido_id="pedido-1",
            monto=Dinero(Decimal(0)),
            metodo=MetodoPago.EFECTIVO,
        )


@pytest.mark.parametrize(
    ("metodo", "referencia"),
    [
        (MetodoPago.TARJETA, ""),
        (MetodoPago.TRANSFERENCIA, "   "),
        (MetodoPago.YAPE, ""),
    ],
)
def test_exige_referencia_para_metodos_trazables(
    metodo: MetodoPago,
    referencia: str,
) -> None:
    with pytest.raises(ReferenciaPagoInvalida):
        PagoFactory.crear(
            pedido_id="pedido-1",
            monto=Dinero(Decimal(10)),
            metodo=metodo,
            referencia=referencia,
        )


def test_efectivo_permite_referencia_vacia() -> None:
    pago = PagoFactory.crear(
        pedido_id="pedido-1",
        monto=Dinero(Decimal(10)),
        metodo=MetodoPago.EFECTIVO,
    )

    assert pago.referencia == ""


@pytest.mark.parametrize("metodo", list(MetodoPago))
def test_admite_todos_los_metodos_soportados(metodo: MetodoPago) -> None:
    referencia = "" if metodo == MetodoPago.EFECTIVO else "referencia-1"

    pago = PagoFactory.crear(
        pedido_id="pedido-1",
        monto=Dinero(Decimal(10)),
        metodo=metodo,
        referencia=referencia,
    )

    assert pago.metodo == metodo


def test_rechaza_metodo_no_soportado() -> None:
    with pytest.raises(MetodoPagoNoSoportado):
        PagoFactory.crear(
            pedido_id="pedido-1",
            monto=Dinero(Decimal(10)),
            metodo="criptomoneda",
        )


def test_rechaza_identificadores_obligatorios_vacios() -> None:
    with pytest.raises(IdentificadorPagoInvalido):
        Pago(
            id=" ",
            pedido_id="pedido-1",
            monto=Dinero(Decimal(10)),
            metodo=MetodoPago.EFECTIVO,
        )

    with pytest.raises(PedidoPagoInvalido):
        PagoFactory.crear(
            pedido_id=" ",
            monto=Dinero(Decimal(10)),
            metodo=MetodoPago.EFECTIVO,
        )


def test_rechaza_datos_mayores_que_el_esquema() -> None:
    with pytest.raises(LongitudDatoPagoInvalida):
        PagoFactory.crear(
            pedido_id="p" * 37,
            monto=Dinero(Decimal(10)),
            metodo=MetodoPago.EFECTIVO,
        )

    with pytest.raises(LongitudDatoPagoInvalida):
        PagoFactory.crear(
            pedido_id="pedido-1",
            monto=Dinero(Decimal(10)),
            metodo=MetodoPago.TARJETA,
            referencia="r" * 121,
        )


def test_factory_admite_politica_extensible() -> None:
    validador = ValidadorMetodoPago([ReferenciaTransferenciaPersonalizada()])

    pago = PagoFactory.crear(
        pedido_id="pedido-1",
        monto=Dinero(Decimal(10)),
        metodo=MetodoPago.TRANSFERENCIA,
        referencia="123",
        validador_metodo=validador,
    )

    assert pago.referencia == "EXT-123"


def test_validador_rechaza_politicas_duplicadas() -> None:
    with pytest.raises(ValueError, match="mas de una politica"):
        ValidadorMetodoPago([ReferenciaObligatoria(), ReferenciaObligatoria()])
