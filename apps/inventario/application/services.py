"""Servicios de aplicacion para inventario."""

from django.db import IntegrityError, transaction

from apps.catalogo.domain.repositorios import RepositorioCatalogo, RepositorioVariante
from apps.inventario.domain.consultas import (
    CategoriaStockAgrupada,
    VarianteStockBajoMinimo,
)
from apps.inventario.domain.excepciones import (
    CategoriaNoEncontradaError,
    StockNoEncontradoError,
    StockYaExisteError,
    VarianteNoEncontradaError,
)
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
    """Coordina el stock de cada variante y su historico de movimientos.

    Todo caso de uso que modifique existencias corre dentro de una
    transaccion y lee el stock con bloqueo: el saldo se calcula en memoria a
    partir de lo leido, asi que sin serializar el acceso dos operaciones
    simultaneas sobre la misma variante se pisarian.
    """

    def __init__(
        self,
        repo_inventario: RepositorioInventario,
        repo_movimientos: RepositorioMovimientoInventario,
        repo_alertas: RepositorioAlertaStock,
        repo_variante: RepositorioVariante | None = None,
        repo_catalogo: RepositorioCatalogo | None = None,
    ) -> None:
        self.repo_inventario = repo_inventario
        self.repo_movimientos = repo_movimientos
        self.repo_alertas = repo_alertas
        self.repo_variante = repo_variante
        self.repo_catalogo = repo_catalogo

    def crear_stock(
        self,
        variante_id: str,
        stock_inicial: int,
        stock_minimo: int,
        ubicacion: str = "almacen",
    ) -> StockVariante:
        with transaction.atomic():
            self._validar_variante_existente(variante_id)
            if self.repo_inventario.buscar_por_variante(variante_id) is not None:
                raise StockYaExisteError("Ya existe stock para la variante")

            stock = InventarioFabrica.crear(
                variante_id,
                stock_inicial,
                stock_minimo,
                ubicacion,
            )
            try:
                self.repo_inventario.guardar(stock)
            except IntegrityError as exc:
                # La unicidad de `stocks_variante.variante_id` cierra la
                # ventana entre la comprobacion anterior y esta escritura.
                raise StockYaExisteError("Ya existe stock para la variante") from exc

            self._generar_alerta_si_corresponde(stock)
            return stock

    def consultar_stock(self, variante_id: str) -> StockVariante | None:
        return self.repo_inventario.buscar_por_variante(variante_id)

    def listar_stock(self) -> list[StockVariante]:
        return self.repo_inventario.listar()

    def listar_stock_por_categoria(
        self,
        categoria_id: str | None = None,
    ) -> list[CategoriaStockAgrupada]:
        if (
            categoria_id
            and self.repo_catalogo is not None
            and self.repo_catalogo.buscar_categoria(categoria_id) is None
        ):
            raise CategoriaNoEncontradaError("La categoria no existe")
        return self.repo_inventario.listar_por_categoria(categoria_id)

    def listar_stock_bajo_minimo(self) -> list[VarianteStockBajoMinimo]:
        """Variantes que hay que reponer, no prendas: falta la talla concreta."""
        return self.repo_inventario.listar_bajo_minimo()

    def registrar_ingreso(
        self,
        variante_id: str,
        cantidad: int,
        motivo: str,
        usuario_id: str,
    ) -> MovimientoInventario:
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(variante_id)
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
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(variante_id)
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
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(variante_id)
            movimiento = stock.ajustar(nueva_cantidad, motivo, usuario_id)
            self.repo_inventario.guardar(stock)
            self.repo_movimientos.guardar(movimiento)
            self._generar_alerta_si_corresponde(stock)
            return movimiento

    def reservar(self, variante_id: str, cantidad: int) -> StockVariante:
        """Compromete unidades al confirmar un pedido."""
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(variante_id)
            stock.reservar(cantidad)
            self.repo_inventario.guardar(stock)
            return stock

    def liberar(self, variante_id: str, cantidad: int) -> StockVariante:
        """Devuelve al disponible lo reservado por un pedido cancelado."""
        with transaction.atomic():
            stock = self._obtener_stock_bloqueado(variante_id)
            stock.liberar(cantidad)
            self.repo_inventario.guardar(stock)
            return stock

    def listar_movimientos(self, stock_id: str) -> list[MovimientoInventario]:
        return self.repo_movimientos.listar_por_stock(stock_id)

    def _generar_alerta_si_corresponde(self, stock: StockVariante) -> None:
        alerta = stock.generar_alerta_si_corresponde()
        if alerta and self.repo_alertas.buscar_pendiente_por_stock(stock.id) is None:
            self.repo_alertas.guardar(alerta)

    def _obtener_stock_bloqueado(self, variante_id: str) -> StockVariante:
        stock = self.repo_inventario.buscar_por_variante_bloqueada(variante_id)
        if stock is None:
            raise StockNoEncontradoError("No existe stock para la variante")
        return stock

    def _validar_variante_existente(self, variante_id: str) -> None:
        if self.repo_variante is None:
            return
        if self.repo_variante.buscar_por_id(variante_id) is None:
            raise VarianteNoEncontradaError("La variante no existe")
