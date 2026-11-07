"""Suite de servicio: ServicioDespachos con dobles de prueba (Lab 05).

Se reemplazan por mocks el repositorio de despachos, el lector de pedidos y
los repositorios de inventario; la unidad de trabajo es un MagicMock que
actua como context manager. Se verifican estados e interacciones.
"""

from decimal import Decimal
from unittest.mock import MagicMock, create_autospec

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoDespacho
from apps.inventario.domain.repositorios import (
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from apps.inventario.domain.stock_prenda import InventarioFabrica
from apps.ventas.despachos.application.services import ServicioDespachos
from apps.ventas.despachos.domain.despacho import DespachoFabrica
from apps.ventas.despachos.domain.errors import (
    DespachoNoEncontradoError,
    DespachoYaExisteError,
    PedidoNoPagadoError,
)
from apps.ventas.despachos.domain.repositorios import RepositorioDespacho
from apps.ventas.pedidos.domain.pedido import DetallePedido, PedidoFactory
from apps.ventas.pedidos.domain.repositorios import LectorPedido


class TestServicioDespachosConMocks:
    def setup_method(self) -> None:
        self.repo_despachos = create_autospec(RepositorioDespacho, instance=True)
        self.repo_pedidos = create_autospec(LectorPedido, instance=True)
        self.inventario = create_autospec(RepositorioInventario, instance=True)
        self.movimientos = create_autospec(
            RepositorioMovimientoInventario, instance=True
        )
        self.unidad_trabajo = MagicMock()
        self.servicio = ServicioDespachos(
            self.repo_despachos,
            self.repo_pedidos,
            self.unidad_trabajo,
            self.inventario,
            self.movimientos,
        )
        self.pedido = PedidoFactory.crear(
            "cliente-1",
            "carrito-1",
            [DetallePedido("variante-1", 2, Dinero(Decimal("25.00")))],
        )
        self.repo_pedidos.buscar_por_id_para_actualizar.return_value = self.pedido

    def test_programar_pedido_pagado_guarda_despacho(self) -> None:
        self.pedido.marcar_pagado()
        self.repo_despachos.buscar_por_pedido.return_value = None

        despacho = self.servicio.programar(self.pedido.id, "Av. Goyeneche 300")

        assert despacho.estado == EstadoDespacho.PENDIENTE
        self.repo_despachos.guardar.assert_called_once_with(despacho)
        self.unidad_trabajo.return_value.__exit__.assert_called_once()

    def test_no_programa_pedido_sin_pagar(self) -> None:
        with pytest.raises(PedidoNoPagadoError):
            self.servicio.programar(self.pedido.id, "Av. Goyeneche 300")

        self.repo_despachos.buscar_por_pedido.assert_not_called()
        self.repo_despachos.guardar.assert_not_called()

    def test_no_programa_dos_despachos_del_mismo_pedido(self) -> None:
        self.pedido.marcar_pagado()
        self.repo_despachos.buscar_por_pedido.return_value = DespachoFabrica.crear(
            self.pedido.id, "Otra direccion"
        )

        with pytest.raises(DespachoYaExisteError):
            self.servicio.programar(self.pedido.id, "Av. Goyeneche 300")

        self.repo_despachos.guardar.assert_not_called()

    def test_confirmar_descuenta_la_reserva_y_registra_movimiento(self) -> None:
        despacho = DespachoFabrica.crear(self.pedido.id, "Av. Goyeneche 300")
        despacho.preparar("encargado-1")
        self.repo_despachos.buscar_por_id_para_actualizar.return_value = despacho
        stock = InventarioFabrica.crear("variante-1", 10, 1)
        stock.reservar(2)
        self.inventario.buscar_por_variante_bloqueada.return_value = stock

        self.servicio.confirmar(despacho.id, "T001", "000777")

        assert (stock.cantidad_actual, stock.cantidad_reservada) == (8, 0)
        self.inventario.guardar.assert_called_once_with(stock)
        movimiento = self.movimientos.guardar.call_args.args[0]
        assert movimiento.cantidad == 2
        assert movimiento.registrado_por == "encargado-1"
        self.repo_despachos.guardar.assert_called_once_with(despacho)

    def test_preparar_despacho_inexistente(self) -> None:
        self.repo_despachos.buscar_por_id_para_actualizar.return_value = None

        with pytest.raises(DespachoNoEncontradoError):
            self.servicio.preparar("despacho-x", "encargado-1")

        self.repo_despachos.guardar.assert_not_called()
