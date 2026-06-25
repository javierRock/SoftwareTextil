from pytest import raises

from software_textil.application.dtos.comandos import CrearStockDTO, MovimientoStockDTO
from software_textil.application.services.servicio_inventario import ServicioInventario
from software_textil.domain.inventario.stock_prenda import InventarioFabrica
from software_textil.infrastructure.repositories.in_memory import (
    InMemoryAlertaStockRepository,
    InMemoryInventarioRepository,
    InMemoryMovimientoRepository,
)


def test_inventario_rechaza_stock_inicial_negativo():
    with raises(ValueError, match="stock inicial"):
        InventarioFabrica.crear("prenda-1", -1, 0, "almacen")


def test_servicio_inventario_no_duplica_alertas_pendientes():
    inventario = InMemoryInventarioRepository()
    movimientos = InMemoryMovimientoRepository()
    alertas = InMemoryAlertaStockRepository()
    servicio = ServicioInventario(inventario, movimientos, alertas)

    servicio.crear_stock(CrearStockDTO("prenda-1", 5, 5))
    servicio.registrar_salida(MovimientoStockDTO("prenda-1", 1, "venta", "usuario-1"))
    servicio.registrar_salida(MovimientoStockDTO("prenda-1", 1, "venta", "usuario-1"))

    assert len(alertas.items) == 1
    assert len(movimientos.items) == 2
