"""Pruebas del servicio de aplicacion de inventario."""

import pytest

from apps.compartido.domain.enums import TipoMovimiento
from apps.inventario.domain.excepciones import PrendaNoEncontrada, StockInsuficiente, StockNoEncontrado
from apps.inventario.infrastructure.models import MovimientoInventarioModel
from apps.inventario.infrastructure.repositories import DjangoRepositorioMovimiento


@pytest.mark.django_db
def test_segundo_ingreso_se_acumula_sobre_el_stock_actual(servicio_inventario, stock, prenda) -> None:
    movimiento_1 = servicio_inventario.registrar_ingreso("prenda-1", 5, "Ingreso 1", "usuario-1")
    movimiento_2 = servicio_inventario.registrar_ingreso("prenda-1", 2, "Ingreso 2", "usuario-1")

    stock.refresh_from_db()

    assert stock.cantidad_actual == 17
    assert MovimientoInventarioModel.objects.count() == 2
    assert movimiento_1.tipo == TipoMovimiento.INGRESO
    assert movimiento_2.tipo == TipoMovimiento.INGRESO


@pytest.mark.django_db
def test_stock_no_encontrado_levanta_excepcion(servicio_inventario, prenda) -> None:
    with pytest.raises(PrendaNoEncontrada):
        servicio_inventario.registrar_ingreso("prenda-inexistente", 1, "Ingreso", "usuario-1")


@pytest.mark.django_db
def test_salida_sin_stock_levanta_excepcion(servicio_inventario, categoria) -> None:
    from apps.catalogo.infrastructure.models import PrendaModel

    PrendaModel.objects.create(
        id="prenda-sin-stock",
        nombre="Polo sin stock",
        descripcion="Prenda existente sin registro de stock",
        precio_monto="25.00",
        precio_moneda="PEN",
        categoria=categoria,
        estado="activa",
        registrado_por="usuario-1",
    )

    with pytest.raises(StockNoEncontrado):
        servicio_inventario.registrar_salida("prenda-sin-stock", 1, "Salida", "usuario-1")


@pytest.mark.django_db
def test_salida_insuficiente_no_modifica_stock(servicio_inventario, stock, prenda) -> None:
    with pytest.raises(StockInsuficiente):
        servicio_inventario.registrar_salida("prenda-1", 11, "Salida", "usuario-1")

    stock.refresh_from_db()
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_fallo_al_guardar_movimiento_revierte_stock(monkeypatch, servicio_inventario, stock, prenda) -> None:
    def _fallar_guardado(self, movimiento):
        raise RuntimeError("fallo al guardar movimiento")

    monkeypatch.setattr(DjangoRepositorioMovimiento, "guardar", _fallar_guardado)

    with pytest.raises(RuntimeError):
        servicio_inventario.registrar_ingreso("prenda-1", 5, "Ingreso", "usuario-1")

    stock.refresh_from_db()
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_fallo_al_guardar_movimiento_en_salida_revierte_stock(monkeypatch, servicio_inventario, stock, prenda) -> None:
    def _fallar_guardado(self, movimiento):
        raise RuntimeError("fallo al guardar movimiento")

    monkeypatch.setattr(DjangoRepositorioMovimiento, "guardar", _fallar_guardado)

    with pytest.raises(RuntimeError):
        servicio_inventario.registrar_salida("prenda-1", 5, "Salida", "usuario-1")

    stock.refresh_from_db()
    assert stock.cantidad_actual == 10
    assert MovimientoInventarioModel.objects.count() == 0


@pytest.mark.django_db
def test_salida_exacta_deja_stock_en_cero(servicio_inventario, stock, prenda) -> None:
    servicio_inventario.registrar_salida("prenda-1", 10, "Salida", "usuario-1")

    stock.refresh_from_db()
    assert stock.cantidad_actual == 0
    assert MovimientoInventarioModel.objects.count() == 1
