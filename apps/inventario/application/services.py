"""Servicios de aplicacion para inventario."""

from apps.compartido.domain.enums import TipoMovimiento
from apps.inventario.domain.stock_prenda import InventarioFabrica, MovimientoInventario, StockPrenda
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioAlertaStock,
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)


class ServicioInventario:
    def __init__(
        self,
        repo_inventario: DjangoRepositorioInventario,
        repo_movimientos: DjangoRepositorioMovimiento,
        repo_alertas: DjangoRepositorioAlertaStock,
    ) -> None:
        self.repo_inventario = repo_inventario
        self.repo_movimientos = repo_movimientos
        self.repo_alertas = repo_alertas

    def crear_stock(self, prenda_id: str, stock_inicial: int, stock_minimo: int, ubicacion: str = "almacen") -> StockPrenda:
        stock = InventarioFabrica.crear(prenda_id, stock_inicial, stock_minimo, ubicacion)
        self.repo_inventario.guardar(stock)
        self._generar_alerta_si_corresponde(stock)
        return stock

    def consultar_stock(self, prenda_id: str) -> StockPrenda | None:
        return self.repo_inventario.buscar_por_prenda(prenda_id)

    def listar_stock(self) -> list[StockPrenda]:
        return self.repo_inventario.listar()

    def registrar_ingreso(self, prenda_id: str, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        stock = self._obtener_stock(prenda_id)
        movimiento = stock.registrar_ingreso(cantidad, motivo, usuario_id)
        self.repo_inventario.guardar(stock)
        self.repo_movimientos.guardar(movimiento)
        return movimiento

    def registrar_salida(self, prenda_id: str, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        stock = self._obtener_stock(prenda_id)
        movimiento = stock.registrar_salida(cantidad, motivo, usuario_id)
        self.repo_inventario.guardar(stock)
        self.repo_movimientos.guardar(movimiento)
        self._generar_alerta_si_corresponde(stock)
        return movimiento

    def ajustar_stock(self, prenda_id: str, nueva_cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        stock = self._obtener_stock(prenda_id)
        movimiento = stock.ajustar(nueva_cantidad, motivo, usuario_id)
        self.repo_inventario.guardar(stock)
        self.repo_movimientos.guardar(movimiento)
        self._generar_alerta_si_corresponde(stock)
        return movimiento

    def listar_movimientos(self, stock_id: str) -> list[MovimientoInventario]:
        return self.repo_movimientos.listar_por_stock(stock_id)

    def _generar_alerta_si_corresponde(self, stock: StockPrenda) -> None:
        alerta = stock.generar_alerta_si_corresponde()
        if alerta and self.repo_alertas.buscar_pendiente_por_stock(stock.id) is None:
            self.repo_alertas.guardar(alerta)

    def _obtener_stock(self, prenda_id: str) -> StockPrenda:
        stock = self.repo_inventario.buscar_por_prenda(prenda_id)
        if stock is None:
            raise ValueError("No existe stock para la prenda")
        return stock
