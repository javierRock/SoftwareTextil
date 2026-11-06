"""Suite de dominio: invariantes del agregado Pedido (Lab 05).

Pruebas unitarias puras: no tocan base de datos ni Django. Cada metodo es un
caso de prueba independiente; `setup_method` reconstruye el estado inicial
antes de cada caso y `teardown_method` lo descarta.
"""

from decimal import Decimal

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPedido
from apps.ventas.pedidos.domain.errors import (
    CantidadDetalleInvalidaError,
    PedidoCanceladoError,
    PedidoNoCancelableError,
    PedidoSinDetallesError,
    PedidoYaCanceladoError,
    PedidoYaPagadoError,
)
from apps.ventas.pedidos.domain.pedido import DetallePedido, PedidoFactory


class TestPedidoDominio:
    def setup_method(self) -> None:
        self.detalles = [
            DetallePedido("variante-a", 2, Dinero(Decimal("30.00"))),
            DetallePedido("variante-b", 1, Dinero(Decimal("15.50"))),
        ]
        self.pedido = PedidoFactory.crear("cliente-1", "carrito-1", self.detalles)

    def teardown_method(self) -> None:
        self.detalles = []
        self.pedido = None

    def test_factory_calcula_total_como_suma_de_subtotales(self) -> None:
        assert self.pedido.total == Dinero(Decimal("75.50"))
        assert self.pedido.estado == EstadoPedido.CREADO

    def test_factory_rechaza_pedido_sin_detalles(self) -> None:
        with pytest.raises(PedidoSinDetallesError):
            PedidoFactory.crear("cliente-1", "carrito-1", [])

    @pytest.mark.parametrize("cantidad", [0, -1])
    def test_detalle_rechaza_cantidad_no_positiva(self, cantidad: int) -> None:
        with pytest.raises(CantidadDetalleInvalidaError):
            DetallePedido("variante-a", cantidad, Dinero(Decimal("10.00")))

    def test_detalle_acepta_cantidad_limite_uno(self) -> None:
        detalle = DetallePedido("variante-a", 1, Dinero(Decimal("10.00")))
        assert detalle.subtotal() == Dinero(Decimal("10.00"))

    def test_cancelar_pedido_creado_cambia_estado(self) -> None:
        self.pedido.cancelar()
        assert self.pedido.estado == EstadoPedido.CANCELADO

    def test_no_se_cancela_un_pedido_pagado(self) -> None:
        self.pedido.marcar_pagado()
        with pytest.raises(PedidoNoCancelableError):
            self.pedido.cancelar()
        assert self.pedido.estado == EstadoPedido.PAGADO

    def test_no_se_cancela_dos_veces(self) -> None:
        self.pedido.cancelar()
        with pytest.raises(PedidoYaCanceladoError):
            self.pedido.cancelar()

    def test_no_se_paga_dos_veces(self) -> None:
        self.pedido.marcar_pagado()
        with pytest.raises(PedidoYaPagadoError):
            self.pedido.marcar_pagado()

    def test_no_se_paga_un_pedido_cancelado(self) -> None:
        self.pedido.cancelar()
        with pytest.raises(PedidoCanceladoError):
            self.pedido.marcar_pagado()
        assert self.pedido.estado == EstadoPedido.CANCELADO
