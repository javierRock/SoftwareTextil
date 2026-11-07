"""Suite de dominio: agregado Despacho y objeto de valor GuiaRemision (Lab 05).

Maquina de estados probada: PENDIENTE -> PREPARADO -> CONFIRMADO, con
CANCELADO como salida; CONFIRMADO y CANCELADO son estados finales.
"""

import pytest

from apps.compartido.domain.enums import EstadoDespacho
from apps.ventas.despachos.domain.despacho import (
    LONGITUD_MAXIMA_DIRECCION,
    LONGITUD_MAXIMA_SERIE,
    DespachoFabrica,
    GuiaRemision,
)
from apps.ventas.despachos.domain.errors import (
    DespachoCanceladoError,
    DespachoConfirmadoError,
    DespachoNoPreparadoError,
    DireccionDespachoInvalidaError,
    GuiaRemisionInvalidaError,
)


class TestDespachoDominio:
    def setup_method(self) -> None:
        self.despacho = DespachoFabrica.crear("pedido-1", "  Av. Ejercito 101  ")
        self.guia = GuiaRemision("T001", "000123", "Olva")

    def teardown_method(self) -> None:
        self.despacho = None

    def test_fabrica_crea_despacho_pendiente_con_direccion_limpia(self) -> None:
        assert self.despacho.estado == EstadoDespacho.PENDIENTE
        assert self.despacho.direccion_entrega == "Av. Ejercito 101"

    @pytest.mark.parametrize("direccion", ["", "   ", "x" * 251])
    def test_direccion_invalida(self, direccion: str) -> None:
        with pytest.raises(DireccionDespachoInvalidaError):
            DespachoFabrica.crear("pedido-1", direccion)

    def test_direccion_en_el_limite_maximo(self) -> None:
        despacho = DespachoFabrica.crear("p", "x" * LONGITUD_MAXIMA_DIRECCION)
        assert len(despacho.direccion_entrega) == LONGITUD_MAXIMA_DIRECCION

    def test_flujo_completo_preparar_y_confirmar(self) -> None:
        self.despacho.preparar("encargado-1")
        self.despacho.confirmar(self.guia)

        assert self.despacho.estado == EstadoDespacho.CONFIRMADO
        assert self.despacho.responsable_id == "encargado-1"
        assert self.despacho.guia.codigo == "T001-000123"
        assert self.despacho.fecha_confirmacion is not None

    def test_no_se_confirma_sin_preparar(self) -> None:
        with pytest.raises(DespachoNoPreparadoError):
            self.despacho.confirmar(self.guia)
        assert self.despacho.guia is None

    def test_confirmado_es_estado_final(self) -> None:
        self.despacho.preparar("encargado-1")
        self.despacho.confirmar(self.guia)
        with pytest.raises(DespachoConfirmadoError):
            self.despacho.cancelar()

    def test_cancelado_no_puede_prepararse(self) -> None:
        self.despacho.cancelar()
        with pytest.raises(DespachoCanceladoError):
            self.despacho.preparar("encargado-1")


class TestGuiaRemision:
    def test_serie_en_el_limite_es_valida(self) -> None:
        guia = GuiaRemision("S" * LONGITUD_MAXIMA_SERIE, "1")
        assert guia.codigo == f"{'S' * LONGITUD_MAXIMA_SERIE}-1"

    @pytest.mark.parametrize(
        ("serie", "numero"),
        [("", "1"), ("S" * (LONGITUD_MAXIMA_SERIE + 1), "1"), ("T001", "12A")],
    )
    def test_guia_invalida(self, serie: str, numero: str) -> None:
        with pytest.raises(GuiaRemisionInvalidaError):
            GuiaRemision(serie, numero)
