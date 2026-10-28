"""Pruebas unitarias del dominio de inventario."""

import pytest

from apps.compartido.domain.enums import TipoMovimiento
from apps.inventario.domain.excepciones import (
    CantidadInvalidaError,
    StockInsuficienteError,
)
from apps.inventario.domain.stock_prenda import InventarioFabrica, StockVariante


def _stock() -> StockVariante:
    return StockVariante(
        id="stock-1",
        variante_id="prenda-1",
        cantidad_actual=10,
        nivel_minimo=3,
        ubicacion="almacen",
        unidad="unidad",
    )


def test_ingreso_incrementa_stock_y_crea_movimiento_ingreso() -> None:
    stock = _stock()

    movimiento = stock.registrar_ingreso(5, "Ingreso de prueba", "usuario-1")

    assert stock.cantidad_actual == 15
    assert movimiento.tipo == TipoMovimiento.INGRESO
    assert movimiento.cantidad == 5
    assert movimiento.stock_id == "stock-1"


def test_salida_descuenta_stock_y_crea_movimiento_salida() -> None:
    stock = _stock()

    movimiento = stock.registrar_salida(4, "Salida de prueba", "usuario-1")

    assert stock.cantidad_actual == 6
    assert movimiento.tipo == TipoMovimiento.SALIDA
    assert movimiento.cantidad == 4


@pytest.mark.parametrize("cantidad", [0, -1])
def test_cantidad_invalida_es_rechazada(cantidad: int) -> None:
    stock = _stock()

    with pytest.raises(CantidadInvalidaError):
        stock.registrar_ingreso(cantidad, "Ingreso", "usuario-1")


def test_salida_con_stock_insuficiente_es_rechazada() -> None:
    stock = _stock()

    with pytest.raises(StockInsuficienteError):
        stock.registrar_salida(11, "Salida", "usuario-1")

    assert stock.cantidad_actual == 10


def test_fabrica_rechaza_stock_inicial_negativo() -> None:
    with pytest.raises(CantidadInvalidaError):
        InventarioFabrica.crear("prenda-1", -1, 3, "almacen")
