"""Suite de servicio: ServicioInventario con dobles de prueba (Lab 05).

Los tres repositorios son mocks con la firma de su contrato. Ademas se usa
`patch` para sustituir `transaction.atomic` de Django: asi el servicio se
prueba en aislamiento total, sin abrir conexion a la base de datos.
"""

from unittest.mock import create_autospec, patch

import pytest

from apps.catalogo.domain.repositorios import RepositorioVariante
from apps.compartido.domain.enums import TipoMovimiento
from apps.inventario.application.services import ServicioInventario
from apps.inventario.domain.excepciones import (
    StockInsuficienteError,
    StockNoEncontradoError,
    StockYaExisteError,
    VarianteNoEncontradaError,
)
from apps.inventario.domain.repositorios import (
    RepositorioAlertaStock,
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from apps.inventario.domain.stock_prenda import AlertaStock, InventarioFabrica

USUARIO = "usuario-1"


class TestServicioInventarioConMocks:
    def setup_method(self) -> None:
        self.parche = patch("apps.inventario.application.services.transaction")
        self.transaccion = self.parche.start()
        self.repo_inventario = create_autospec(RepositorioInventario, instance=True)
        self.repo_movimientos = create_autospec(
            RepositorioMovimientoInventario, instance=True
        )
        self.repo_alertas = create_autospec(RepositorioAlertaStock, instance=True)
        self.repo_variante = create_autospec(RepositorioVariante, instance=True)
        self.servicio = ServicioInventario(
            self.repo_inventario,
            self.repo_movimientos,
            self.repo_alertas,
            repo_variante=self.repo_variante,
        )
        self.stock = InventarioFabrica.crear("variante-1", 10, 3)
        self.repo_inventario.buscar_por_variante_bloqueada.return_value = self.stock
        self.repo_alertas.buscar_pendiente_por_stock.return_value = None

    def teardown_method(self) -> None:
        self.parche.stop()

    def test_registrar_salida_guarda_stock_y_movimiento(self) -> None:
        movimiento = self.servicio.registrar_salida("variante-1", 4, "venta", USUARIO)

        assert movimiento.tipo == TipoMovimiento.SALIDA
        self.repo_inventario.guardar.assert_called_once_with(self.stock)
        self.repo_movimientos.guardar.assert_called_once_with(movimiento)
        self.repo_alertas.guardar.assert_not_called()
        self.transaccion.atomic.assert_called_once()

    def test_salida_bajo_el_minimo_genera_una_alerta(self) -> None:
        self.servicio.registrar_salida("variante-1", 8, "venta", USUARIO)

        self.repo_alertas.buscar_pendiente_por_stock.assert_called_once_with(
            self.stock.id
        )
        alerta = self.repo_alertas.guardar.call_args.args[0]
        assert alerta.nivel_actual == 2

    def test_no_duplica_alerta_si_ya_hay_una_pendiente(self) -> None:
        self.repo_alertas.buscar_pendiente_por_stock.return_value = AlertaStock(
            id="alerta-previa", stock_id=self.stock.id, nivel_actual=2, nivel_minimo=3
        )
        self.servicio.registrar_salida("variante-1", 8, "venta", USUARIO)

        self.repo_alertas.guardar.assert_not_called()

    def test_salida_sin_stock_suficiente_no_persiste(self) -> None:
        with pytest.raises(StockInsuficienteError):
            self.servicio.registrar_salida("variante-1", 11, "venta", USUARIO)

        self.repo_inventario.guardar.assert_not_called()
        self.repo_movimientos.guardar.assert_not_called()

    def test_variante_sin_stock_lanza_error(self) -> None:
        self.repo_inventario.buscar_por_variante_bloqueada.return_value = None

        with pytest.raises(StockNoEncontradoError):
            self.servicio.registrar_ingreso("variante-x", 1, "compra", USUARIO)

    def test_crear_stock_de_variante_inexistente(self) -> None:
        self.repo_variante.buscar_por_id.return_value = None

        with pytest.raises(VarianteNoEncontradaError):
            self.servicio.crear_stock("variante-x", 5, 1)

        self.repo_inventario.guardar.assert_not_called()

    def test_crear_stock_duplicado(self) -> None:
        self.repo_variante.buscar_por_id.return_value = object()
        self.repo_inventario.buscar_por_variante.return_value = self.stock

        with pytest.raises(StockYaExisteError):
            self.servicio.crear_stock("variante-1", 5, 1)

        self.repo_inventario.guardar.assert_not_called()
