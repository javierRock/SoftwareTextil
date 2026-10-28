"""Pruebas de aplicación con dobles de prueba (Laboratorio 05)."""

from contextlib import nullcontext
from decimal import Decimal
from unittest.mock import MagicMock, create_autospec

import pytest

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, EstadoPedido, MetodoPago
from apps.ventas.pagos.application.ports import PedidoParaPago, RepositorioPedidoPago
from apps.ventas.pagos.application.services import ServicioPagos
from apps.ventas.pagos.domain.excepciones import MontoNoCoincideConPedido
from apps.ventas.pagos.domain.pago import Pago, PagoFactory
from apps.ventas.pagos.domain.repositorios import RepositorioPago


def pedido_creado() -> PedidoParaPago:
    return PedidoParaPago(
        id="pedido-double-1",
        cliente_id="cliente-double-1",
        total=Dinero(Decimal("75.00")),
        estado=EstadoPedido.CREADO,
    )


def servicio_con_dobles() -> tuple[
    ServicioPagos,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    repositorio_pago = create_autospec(RepositorioPago, instance=True)
    repositorio_pedido = create_autospec(RepositorioPedidoPago, instance=True)
    unidad_trabajo = MagicMock(name="unidad_trabajo")
    unidad_trabajo.return_value = nullcontext()
    repositorio_pedido.buscar_por_id_para_actualizar.return_value = pedido_creado()
    repositorio_pago.existe_por_pedido.return_value = False
    servicio = ServicioPagos(
        repositorio_pago,
        repositorio_pedido,
        unidad_trabajo,
    )
    return servicio, repositorio_pago, repositorio_pedido, unidad_trabajo


def test_registrar_pago_usa_repositorios_como_dobles() -> None:
    # Arrange
    servicio, pagos, pedidos, unidad_trabajo = servicio_con_dobles()

    # Act
    resultado = servicio.registrar_pago(
        pedido_id=" pedido-double-1 ",
        monto=Decimal("75.00"),
        metodo=MetodoPago.TRANSFERENCIA,
        cliente_id="cliente-double-1",
        referencia="ref-double-1",
    )

    # Assert
    assert resultado.estado == EstadoPago.PENDIENTE
    pedidos.buscar_por_id_para_actualizar.assert_called_once_with("pedido-double-1")
    pagos.existe_por_pedido.assert_called_once_with("pedido-double-1")
    pagos.crear.assert_called_once_with(resultado)
    unidad_trabajo.assert_called_once_with()


def test_aprobar_pago_verifica_interacciones_y_actualiza_pedido() -> None:
    # Arrange
    servicio, pagos, pedidos, _ = servicio_con_dobles()
    pago = PagoFactory.crear(
        pedido_id="pedido-double-1",
        monto=Dinero(Decimal("75.00")),
        metodo=MetodoPago.TRANSFERENCIA,
        referencia="ref-double-1",
    )
    pagos.buscar_por_id_para_actualizar.return_value = pago

    # Act
    resultado = servicio.aprobar(pago.id)

    # Assert
    assert resultado.estado == EstadoPago.APROBADO
    pagos.actualizar_estado.assert_called_once_with(pago)
    pedidos.marcar_pagado.assert_called_once_with("pedido-double-1")


def test_registrar_pago_rechaza_monto_distinto_sin_persistir() -> None:
    # Arrange
    servicio, pagos, pedidos, _ = servicio_con_dobles()

    # Act / Assert
    with pytest.raises(MontoNoCoincideConPedido):
        servicio.registrar_pago(
            pedido_id="pedido-double-1",
            monto=Decimal("74.99"),
            metodo=MetodoPago.EFECTIVO,
            cliente_id="cliente-double-1",
        )

    pagos.crear.assert_not_called()
    pedidos.buscar_por_id_para_actualizar.assert_called_once_with("pedido-double-1")
