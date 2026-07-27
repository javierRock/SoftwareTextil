"""Servicios de aplicacion para inventario."""

from apps.inventario.domain.repositorios import (
    RepositorioAlertaStock,
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from apps.inventario.domain.stock_prenda import (
    InventarioFabrica,
    MovimientoInventario,
    StockVariante,
)


class ServicioInventario:
    """Coordina el stock de cada variante y su historico de movimientos."""

    def __init__(
        self,
        repo_inventario: RepositorioInventario,
        repo_movimientos: RepositorioMovimientoInventario,
        repo_alertas: RepositorioAlertaStock,
    ) -> None:
        self.repo_inventario = repo_inventario
        self.repo_movimientos = repo_movimientos
        self.repo_alertas = repo_alertas

    def crear_stock(
        self,
        variante_id: str,
        stock_inicial: int,
        stock_minimo: int,
        ubicacion: str = "almacen",
    ) -> StockVariante:
        stock = InventarioFabrica.crear(
            variante_id,
            stock_inicial,
            stock_minimo,
            ubicacion,
        )
        self.repo_inventario.guardar(stock)
        self._generar_alerta_si_corresponde(stock)
        return stock

    def consultar_stock(self, variante_id: str) -> StockVariante | None:
        return self.repo_inventario.buscar_por_variante(variante_id)

    def listar_stock(self) -> list[StockVariante]:
        return self.repo_inventario.listar()

    def registrar_ingreso(
        self,
        variante_id: str,
        cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        stock = self._obtener_stock(variante_id)
        movimiento = stock.registrar_ingreso(cantidad, motivo, usuario_id)
        self.repo_inventario.guardar(stock)
        self.repo_movimientos.guardar(movimiento)
        return movimiento

    def registrar_salida(
        self,
        variante_id: str,
        cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        stock = self._obtener_stock(variante_id)
        movimiento = stock.registrar_salida(cantidad, motivo, usuario_id)
        self.repo_inventario.guardar(stock)
        self.repo_movimientos.guardar(movimiento)
        self._generar_alerta_si_corresponde(stock)
        return movimiento

    def ajustar_stock(
        self,
        variante_id: str,
        nueva_cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        stock = self._obtener_stock(variante_id)
        movimiento = stock.ajustar(nueva_cantidad, motivo, usuario_id)
        self.repo_inventario.guardar(stock)
        self.repo_movimientos.guardar(movimiento)
        self._generar_alerta_si_corresponde(stock)
        return movimiento

    def reservar(self, variante_id: str, cantidad: int) -> StockVariante:
        """Compromete unidades al confirmar un pedido."""
        stock = self._obtener_stock(variante_id)
        stock.reservar(cantidad)
        self.repo_inventario.guardar(stock)
        return stock

    def liberar(self, variante_id: str, cantidad: int) -> StockVariante:
        """Devuelve al disponible lo reservado por un pedido cancelado."""
        stock = self._obtener_stock(variante_id)
        stock.liberar(cantidad)
        self.repo_inventario.guardar(stock)
        return stock

    def listar_movimientos(self, stock_id: str) -> list[MovimientoInventario]:
        return self.repo_movimientos.listar_por_stock(stock_id)

    def _generar_alerta_si_corresponde(self, stock: StockVariante) -> None:
        alerta = stock.generar_alerta_si_corresponde()
        if alerta and self.repo_alertas.buscar_pendiente_por_stock(stock.id) is None:
            self.repo_alertas.guardar(alerta)

    def _obtener_stock(self, variante_id: str) -> StockVariante:
        stock = self.repo_inventario.buscar_por_variante(variante_id)
        if stock is None:
            raise ValueError("No existe stock para la variante")
        return stock
