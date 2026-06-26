"""Casos de uso de inventario."""

from software_textil.application.dtos.comandos import AjustarStockDTO, CrearStockDTO, MovimientoStockDTO
from software_textil.application.errors import NotFoundError
from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.inventario.repositorios import (
    RepositorioAlertaStock,
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from software_textil.domain.inventario.stock_prenda import InventarioFabrica, MovimientoInventario, StockPrenda


class ServicioInventario:
    def __init__(
        self,
        inventario: RepositorioInventario,
        movimientos: RepositorioMovimientoInventario,
        alertas: RepositorioAlertaStock,
        unit_of_work: UnitOfWork | None = None,
    ) -> None:
        self.inventario = inventario
        self.movimientos = movimientos
        self.alertas = alertas
        self.uow = unit_of_work or NoOpUnitOfWork()

    def crear_stock(self, dto: CrearStockDTO) -> StockPrenda:
        with self.uow:
            stock = InventarioFabrica.crear(dto.prenda_id, dto.stock_inicial, dto.stock_minimo, dto.ubicacion)
            self.inventario.guardar(stock)
            alerta = stock.generar_alerta_si_corresponde()
            if alerta and self.alertas.buscar_pendiente_por_stock(stock.id) is None:
                self.alertas.guardar(alerta)
            self.uow.commit()
        return stock

    def consultar_stock(self, prenda_id: str) -> StockPrenda | None:
        return self.inventario.buscar_por_prenda(prenda_id)

    def registrar_ingreso(self, dto: MovimientoStockDTO) -> MovimientoInventario:
        with self.uow:
            stock = self._obtener_stock(dto.prenda_id)
            movimiento = stock.registrar_ingreso(dto.cantidad, dto.motivo, dto.usuario_id)
            self.inventario.guardar(stock)
            self.movimientos.guardar(movimiento)
            self.uow.commit()
        return movimiento

    def registrar_salida(self, dto: MovimientoStockDTO) -> MovimientoInventario:
        with self.uow:
            stock = self._obtener_stock(dto.prenda_id)
            movimiento = stock.registrar_salida(dto.cantidad, dto.motivo, dto.usuario_id)
            self.inventario.guardar(stock)
            self.movimientos.guardar(movimiento)
            alerta = stock.generar_alerta_si_corresponde()
            if alerta and self.alertas.buscar_pendiente_por_stock(stock.id) is None:
                self.alertas.guardar(alerta)
            self.uow.commit()
        return movimiento

    def ajustar_stock(self, dto: AjustarStockDTO) -> MovimientoInventario:
        with self.uow:
            stock = self._obtener_stock(dto.prenda_id)
            movimiento = stock.ajustar(dto.nueva_cantidad, dto.motivo, dto.usuario_id)
            self.inventario.guardar(stock)
            self.movimientos.guardar(movimiento)
            self.uow.commit()
        return movimiento

    def _obtener_stock(self, prenda_id: str) -> StockPrenda:
        stock = self.inventario.buscar_por_prenda(prenda_id)
        if stock is None:
            raise NotFoundError("No existe stock para la prenda")
        return stock
