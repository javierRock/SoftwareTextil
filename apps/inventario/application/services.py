"""Servicios de aplicacion para inventario."""

from django.db import IntegrityError, transaction

from apps.catalogo.domain.repositorios import RepositorioPrenda
from apps.inventario.domain.excepciones import PrendaNoEncontrada, StockNoEncontrado, StockYaExiste
from apps.inventario.domain.repositorios import (
    RepositorioAlertaStock,
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from apps.inventario.domain.stock_prenda import InventarioFabrica, MovimientoInventario, StockPrenda


class ServicioInventario:
    def __init__(
        self,
        repo_inventario: RepositorioInventario,
        repo_movimientos: RepositorioMovimientoInventario,
        repo_alertas: RepositorioAlertaStock,
        repo_prenda: RepositorioPrenda | None = None,
    ) -> None:
        self.repo_inventario = repo_inventario
        self.repo_movimientos = repo_movimientos
        self.repo_alertas = repo_alertas
        self.repo_prenda = repo_prenda

    def crear_stock(self, prenda_id: str, stock_inicial: int, stock_minimo: int, ubicacion: str = "almacen") -> StockPrenda:
        with transaction.atomic():
            self._validar_prenda_existente(prenda_id)

            if self.repo_inventario.buscar_por_prenda(prenda_id) is not None:
                raise StockYaExiste("Ya existe stock para la prenda")

            stock = InventarioFabrica.crear(prenda_id, stock_inicial, stock_minimo, ubicacion)

            try:
                self.repo_inventario.guardar(stock)
            except IntegrityError as exc:
                raise StockYaExiste("Ya existe stock para la prenda") from exc

            self._generar_alerta_si_corresponde(stock)
            return stock

    def consultar_stock(self, prenda_id: str) -> StockPrenda | None:
        return self.repo_inventario.buscar_por_prenda(prenda_id)

    def listar_stock(self) -> list[StockPrenda]:
        return self.repo_inventario.listar()

    def registrar_ingreso(self, prenda_id: str, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(prenda_id)
            movimiento = stock.registrar_ingreso(cantidad, motivo, usuario_id)
            self.repo_inventario.guardar(stock)
            self.repo_movimientos.guardar(movimiento)
            self._generar_alerta_si_corresponde(stock)
            return movimiento

    def registrar_salida(self, prenda_id: str, cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(prenda_id)
            movimiento = stock.registrar_salida(cantidad, motivo, usuario_id)
            self.repo_inventario.guardar(stock)
            self.repo_movimientos.guardar(movimiento)
            self._generar_alerta_si_corresponde(stock)
            return movimiento

    def ajustar_stock(self, prenda_id: str, nueva_cantidad: int, motivo: str, usuario_id: str) -> MovimientoInventario:
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(prenda_id)
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

    def _obtener_stock_bloqueado(self, prenda_id: str) -> StockPrenda:
        if self.repo_prenda is not None and self.repo_prenda.buscar_por_id(prenda_id) is None:
            raise PrendaNoEncontrada("La prenda no existe")

        stock = self.repo_inventario.buscar_por_prenda_bloqueado(prenda_id)
        if stock is None:
            raise StockNoEncontrado("No existe stock para la prenda")
        return stock

    def _validar_prenda_existente(self, prenda_id: str) -> None:
        if self.repo_prenda is not None and self.repo_prenda.buscar_por_id(prenda_id) is None:
            raise PrendaNoEncontrada("La prenda no existe")
