from decimal import Decimal

from pytest import raises

from software_textil.application.dtos.comandos import AgregarItemCarritoDTO, CrearCarritoDTO, CrearPedidoDTO, ProcesarPagoDTO
from software_textil.application.errors import NotFoundError
from software_textil.application.services.servicio_compras import ServicioCompras
from software_textil.application.services.servicio_pagos import ServicioPagos
from software_textil.application.services.servicio_pedidos import ServicioPedidos
from software_textil.domain.compartido.enums import EstadoCarrito, EstadoPago, EstadoPedido
from software_textil.infrastructure.repositories.in_memory import (
    InMemoryCarritoRepository,
    InMemoryPagoRepository,
    InMemoryPedidoRepository,
)
from software_textil.infrastructure.unit_of_work import InMemoryUnitOfWork


def test_flujo_carrito_pedido_pago():
    carritos = InMemoryCarritoRepository()
    pedidos = InMemoryPedidoRepository()
    pagos = InMemoryPagoRepository()
    uow = InMemoryUnitOfWork()
    compras = ServicioCompras(carritos, uow)
    servicio_pedidos = ServicioPedidos(pedidos, carritos, uow)
    servicio_pagos = ServicioPagos(pagos, pedidos, uow)

    carrito = compras.crear_carrito(CrearCarritoDTO("cliente-1"))
    compras.agregar_item(AgregarItemCarritoDTO(carrito.id, "prenda-1", 2, Decimal("35.50")))

    pedido = servicio_pedidos.generar_desde_carrito(CrearPedidoDTO(carrito.id, "cliente-1"))
    pago = servicio_pagos.procesar_pago(ProcesarPagoDTO(pedido.id, Decimal("71.00"), "yape"))

    assert carrito.estado == EstadoCarrito.CONVERTIDO
    assert pedido.estado == EstadoPedido.PAGADO
    assert pedido.total.monto == Decimal("71.00")
    assert pago.estado == EstadoPago.APROBADO
    assert uow.commits == 4


def test_unit_of_work_registra_rollback_si_falla_caso_de_uso():
    carritos = InMemoryCarritoRepository()
    uow = InMemoryUnitOfWork()
    compras = ServicioCompras(carritos, uow)

    with raises(NotFoundError):
        compras.agregar_item(AgregarItemCarritoDTO("no-existe", "prenda-1", 1, Decimal("10.00")))

    assert uow.commits == 0
    assert uow.rollbacks == 1


def test_no_permite_pagar_dos_veces_el_mismo_pedido():
    carritos = InMemoryCarritoRepository()
    pedidos = InMemoryPedidoRepository()
    pagos = InMemoryPagoRepository()
    compras = ServicioCompras(carritos)
    servicio_pedidos = ServicioPedidos(pedidos, carritos)
    servicio_pagos = ServicioPagos(pagos, pedidos)

    carrito = compras.crear_carrito(CrearCarritoDTO("cliente-1"))
    compras.agregar_item(AgregarItemCarritoDTO(carrito.id, "prenda-1", 1, Decimal("20.00")))
    pedido = servicio_pedidos.generar_desde_carrito(CrearPedidoDTO(carrito.id, "cliente-1"))
    servicio_pagos.procesar_pago(ProcesarPagoDTO(pedido.id, Decimal("20.00"), "tarjeta"))

    with raises(ValueError, match="pago aprobado"):
        servicio_pagos.procesar_pago(ProcesarPagoDTO(pedido.id, Decimal("20.00"), "tarjeta"))
