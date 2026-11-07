"""Suite de dominio: invariantes del agregado Prenda y sus variantes (Lab 05).

Se aplican valores limite sobre las reglas del dominio (longitud del nombre,
precio mayor que cero, codigo de moneda) y se prueba la unicidad de variantes.
"""

from decimal import Decimal

import pytest

from apps.catalogo.domain.excepciones import ValidacionError
from apps.catalogo.domain.prenda import (
    LONGITUD_MAXIMA_NOMBRE,
    PrendaFabrica,
    VarianteFabrica,
    VariantePrenda,
)
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


def _crear(nombre: str = "Polo basico", precio: str = "39.90", moneda: str = "PEN"):
    return PrendaFabrica.crear(
        nombre=nombre,
        descripcion="Algodon pima",
        precio=Dinero(Decimal(precio), moneda),
        categoria_id="categoria-1",
        registrado_por=None,
        tallas=["S", "M"],
    )


class TestPrendaDominio:
    def setup_method(self) -> None:
        self.prenda = _crear()

    def test_fabrica_crea_prenda_activa_con_variantes(self) -> None:
        assert self.prenda.estado == EstadoPrenda.ACTIVA
        assert self.prenda.tallas == ["S", "M"]

    def test_nombre_en_el_limite_maximo_es_valido(self) -> None:
        prenda = _crear(nombre="x" * LONGITUD_MAXIMA_NOMBRE)
        assert len(prenda.nombre) == LONGITUD_MAXIMA_NOMBRE

    def test_nombre_que_excede_el_limite_es_rechazado(self) -> None:
        with pytest.raises(ValidacionError):
            _crear(nombre="x" * (LONGITUD_MAXIMA_NOMBRE + 1))

    def test_nombre_vacio_es_rechazado(self) -> None:
        with pytest.raises(ValidacionError):
            _crear(nombre="   ")

    @pytest.mark.parametrize("precio", ["0", "0.00"])
    def test_precio_cero_es_rechazado(self, precio: str) -> None:
        with pytest.raises(ValidacionError):
            _crear(precio=precio)

    def test_precio_minimo_positivo_es_valido(self) -> None:
        assert _crear(precio="0.01").precio.monto == Decimal("0.01")

    @pytest.mark.parametrize("moneda", ["pen", "PE", "PENS", "P3N"])
    def test_moneda_debe_ser_codigo_de_tres_letras_mayusculas(
        self, moneda: str
    ) -> None:
        with pytest.raises(ValidacionError):
            _crear(moneda=moneda)

    def test_no_se_repite_talla_y_color(self) -> None:
        with pytest.raises(ValidacionError):
            self.prenda.agregar_variante(VarianteFabrica.crear(self.prenda.id, "s"))
        assert self.prenda.tallas == ["S", "M"]

    def test_desactivar_prenda(self) -> None:
        self.prenda.desactivar()
        assert self.prenda.estado == EstadoPrenda.INACTIVA


class TestVariantePrenda:
    def test_normaliza_talla_y_color_y_genera_sku(self) -> None:
        variante = VariantePrenda(
            id="v-1", prenda_id="abcd1234-ffff", talla=" m ", color="azul marino"
        )
        assert (variante.talla, variante.color) == ("M", "AZUL MARINO")
        assert variante.sku == "ABCD1234-M-AZULMARINO"

    def test_talla_reservada_unica_es_rechazada(self) -> None:
        with pytest.raises(ValidacionError):
            VariantePrenda(id="v-1", prenda_id="p-1", talla="unica")

    def test_precio_efectivo_usa_el_de_la_prenda_si_no_tiene_propio(self) -> None:
        variante = VariantePrenda(id="v-1", prenda_id="p-1", talla="L")
        precio_prenda = Dinero(Decimal("50.00"))
        assert variante.precio_efectivo(precio_prenda) == precio_prenda
