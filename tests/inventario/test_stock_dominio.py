"""Suite de dominio: invariantes de StockVariante (Lab 05).

Reglas probadas: disponible = actual - reservado; no se reserva ni se saca mas
de lo disponible; no se libera ni despacha mas de lo reservado; el ajuste no
puede quedar por debajo de la reserva; la alerta aparece bajo el minimo.
"""

import pytest

from apps.compartido.domain.enums import TipoMovimiento
from apps.inventario.domain.excepciones import (
    CantidadInvalidaError,
    ReservaInvalidaError,
    StockInsuficienteError,
)
from apps.inventario.domain.stock_prenda import InventarioFabrica

USUARIO = "usuario-1"


class TestStockVariante:
    def setup_method(self) -> None:
        self.stock = InventarioFabrica.crear("variante-1", 10, 3)

    def teardown_method(self) -> None:
        self.stock = None

    def test_reservar_reduce_disponible_sin_tocar_actual(self) -> None:
        self.stock.reservar(4)
        assert self.stock.cantidad_actual == 10
        assert self.stock.cantidad_disponible == 6

    def test_reservar_exactamente_lo_disponible(self) -> None:
        self.stock.reservar(10)
        assert self.stock.cantidad_disponible == 0

    def test_reservar_mas_de_lo_disponible_falla(self) -> None:
        with pytest.raises(StockInsuficienteError):
            self.stock.reservar(11)
        assert self.stock.cantidad_reservada == 0

    @pytest.mark.parametrize("cantidad", [0, -2])
    def test_cantidades_no_positivas_son_invalidas(self, cantidad: int) -> None:
        with pytest.raises(CantidadInvalidaError):
            self.stock.registrar_ingreso(cantidad, "compra", USUARIO)

    def test_salida_no_puede_usar_unidades_reservadas(self) -> None:
        self.stock.reservar(8)
        with pytest.raises(StockInsuficienteError):
            self.stock.registrar_salida(3, "venta mostrador", USUARIO)

    def test_ingreso_genera_movimiento_de_tipo_ingreso(self) -> None:
        movimiento = self.stock.registrar_ingreso(5, "compra", USUARIO)
        assert self.stock.cantidad_actual == 15
        assert movimiento.tipo == TipoMovimiento.INGRESO
        assert movimiento.stock_id == self.stock.id

    def test_liberar_mas_de_lo_reservado_falla(self) -> None:
        self.stock.reservar(2)
        with pytest.raises(ReservaInvalidaError):
            self.stock.liberar(3)

    def test_despachar_reserva_descuenta_actual_y_reservado(self) -> None:
        self.stock.reservar(4)
        self.stock.despachar_reserva(4, "despacho", USUARIO)
        assert (self.stock.cantidad_actual, self.stock.cantidad_reservada) == (6, 0)

    def test_ajuste_no_puede_quedar_bajo_lo_reservado(self) -> None:
        self.stock.reservar(5)
        with pytest.raises(ReservaInvalidaError):
            self.stock.ajustar(4, "conteo fisico", USUARIO)

    def test_alerta_solo_cuando_actual_es_menor_al_minimo(self) -> None:
        self.stock.registrar_salida(7, "venta", USUARIO)
        assert self.stock.generar_alerta_si_corresponde() is None  # 3 == minimo
        self.stock.registrar_salida(1, "venta", USUARIO)
        alerta = self.stock.generar_alerta_si_corresponde()
        assert (alerta.nivel_actual, alerta.nivel_minimo) == (2, 3)

    def test_fabrica_rechaza_stock_inicial_negativo(self) -> None:
        with pytest.raises(CantidadInvalidaError):
            InventarioFabrica.crear("variante-1", -1, 0)
