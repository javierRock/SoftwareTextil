"""Pruebas del servicio de aplicacion de inventario."""

import pytest

from apps.compartido.domain.enums import TipoMovimiento
from apps.inventario.domain.excepciones import (
    StockInsuficienteError,
    StockNoEncontradoError,
    StockYaExisteError,
    VarianteNoEncontradaError,
)
from apps.inventario.infrastructure.models import MovimientoInventarioModel
from apps.inventario.infrastructure.repositories import DjangoRepositorioMovimiento

pytestmark = pytest.mark.django_db

VARIANTE_INEXISTENTE = "00000000-0000-4000-8000-000000000000"


def test_segundo_ingreso_se_acumula_sobre_el_stock_actual(
    servicio_inventario,
    stock,
    variante_id,
    usuario_id,
) -> None:
    movimiento_1 = servicio_inventario.registrar_ingreso(
        variante_id, 5, "Ingreso 1", usuario_id
    )
    movimiento_2 = servicio_inventario.registrar_ingreso(
        variante_id, 2, "Ingreso 2", usuario_id
    )

    stock.refresh_from_db()

    assert stock.cantidad_actual == 17
    assert MovimientoInventarioModel.objects.count() == 2
    assert movimiento_1.tipo == TipoMovimiento.INGRESO
    assert movimiento_2.tipo == TipoMovimiento.INGRESO


def test_crear_stock_duplicado_es_rechazado_por_el_servicio(
    servicio_inventario,
    stock,
    variante_id,
) -> None:
    with pytest.raises(StockYaExisteError):
        servicio_inventario.crear_stock(variante_id, 5, 1, "almacen")

    stock.refresh_from_db()
    assert stock.cantidad_actual == 10


def test_variante_inexistente_levanta_excepcion(servicio_inventario) -> None:
    with pytest.raises(VarianteNoEncontradaError):
        servicio_inventario.crear_stock(VARIANTE_INEXISTENTE, 1, 0, "almacen")


def test_salida_sin_stock_levanta_excepcion(
    servicio_inventario,
    crear_variante,
    usuario_id,
) -> None:
    """La variante existe en el catalogo pero nunca se le registro stock."""
    variante_sin_stock = crear_variante(talla="XL")

    with pytest.raises(StockNoEncontradoError):
        servicio_inventario.registrar_salida(
            str(variante_sin_stock.id), 1, "Salida", usuario_id
        )


def test_salida_insuficiente_no_modifica_stock(
    servicio_inventario,
    stock,
    variante_id,
    usuario_id,
) -> None:
    with pytest.raises(StockInsuficienteError):
        servicio_inventario.registrar_salida(variante_id, 11, "Salida", usuario_id)

    stock.refresh_from_db()
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


def test_fallo_al_guardar_movimiento_revierte_stock(
    monkeypatch,
    servicio_inventario,
    stock,
    variante_id,
    usuario_id,
) -> None:
    """La transaccion es lo que impide que el stock quede descuadrado."""

    def _fallar_guardado(self, movimiento):
        raise RuntimeError("fallo al guardar movimiento")

    monkeypatch.setattr(DjangoRepositorioMovimiento, "guardar", _fallar_guardado)

    with pytest.raises(RuntimeError):
        servicio_inventario.registrar_ingreso(variante_id, 5, "Ingreso", usuario_id)

    stock.refresh_from_db()
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


def test_fallo_al_guardar_movimiento_en_salida_revierte_stock(
    monkeypatch,
    servicio_inventario,
    stock,
    variante_id,
    usuario_id,
) -> None:
    def _fallar_guardado(self, movimiento):
        raise RuntimeError("fallo al guardar movimiento")

    monkeypatch.setattr(DjangoRepositorioMovimiento, "guardar", _fallar_guardado)

    with pytest.raises(RuntimeError):
        servicio_inventario.registrar_salida(variante_id, 5, "Salida", usuario_id)

    stock.refresh_from_db()
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


def test_salida_exacta_deja_stock_en_cero(
    servicio_inventario,
    stock,
    variante_id,
    usuario_id,
) -> None:
    servicio_inventario.registrar_salida(variante_id, 10, "Salida", usuario_id)

    stock.refresh_from_db()
    assert stock.cantidad_actual == 0
    assert MovimientoInventarioModel.objects.count() == 1


def test_reserva_no_permite_comprometer_mas_del_disponible(
    servicio_inventario,
    stock,
    variante_id,
) -> None:
    servicio_inventario.reservar(variante_id, 4)

    with pytest.raises(StockInsuficienteError):
        servicio_inventario.reservar(variante_id, 7)

    stock.refresh_from_db()
    assert stock.cantidad_reservada == 4
