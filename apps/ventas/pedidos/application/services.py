"""Casos de uso de escritura de pedidos.

Este servicio solo genera y cancela pedidos: las consultas viven en
`apps.ventas.pedidos.application.consultas` (SRP). Depende de contratos del
dominio, nunca de Django ni del ORM (DIP), y declara unicamente los roles de
lectura y escritura que usa, no los de catalogo (ISP).
"""

from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from operator import attrgetter

from apps.inventario.domain.excepciones import StockNoEncontradoError
from apps.inventario.domain.repositorios import RepositorioInventario
from apps.inventario.domain.stock_prenda import StockVariante
from apps.ventas.carrito.domain.carrito import CarritoCompras
from apps.ventas.carrito.domain.repositorios import EscritorCarrito, LectorCarrito
from apps.ventas.pedidos.domain.errors import (
    CarritoNoEncontradoError,
    CarritoNoPerteneceAClienteError,
    PedidoNoEncontradoError,
    PedidoNoPerteneceAClienteError,
)
from apps.ventas.pedidos.domain.pedido import DetallePedido, Pedido, PedidoFactory
from apps.ventas.pedidos.domain.repositorios import EscritorPedido, LectorPedido

AjusteStock = Callable[[StockVariante, int], None]


class ServicioPedidos:
    def __init__(  # noqa: PLR0913, PLR0917
        self,
        lector_pedido: LectorPedido,
        escritor_pedido: EscritorPedido,
        lector_carrito: LectorCarrito,
        escritor_carrito: EscritorCarrito,
        inventario: RepositorioInventario | None = None,
        unidad_trabajo: Callable[[], AbstractContextManager] = nullcontext,
    ) -> None:
        self._lector_pedido = lector_pedido
        self._escritor_pedido = escritor_pedido
        self._lector_carrito = lector_carrito
        self._escritor_carrito = escritor_carrito
        self._inventario = inventario
        self._unidad_trabajo = unidad_trabajo

    def generar_desde_carrito(self, carrito_id: str, cliente_id: str) -> Pedido:
        with self._unidad_trabajo():
            carrito = self._obtener_carrito_del_cliente(carrito_id, cliente_id)
            detalles = self._construir_detalles(carrito)
            pedido = PedidoFactory.crear(
                cliente_id=cliente_id, carrito_id=carrito_id, detalles=detalles
            )
            # El carrito se bloquea antes de validar y todas las reservas se
            # completan antes de persistir el pedido.
            carrito.marcar_convertido()
            self._reservar(detalles)
            self._escritor_pedido.guardar(pedido)
            self._escritor_carrito.guardar(carrito)
        return pedido

    def cancelar(self, pedido_id: str, cliente_id: str | None = None) -> Pedido:
        with self._unidad_trabajo():
            pedido = self._lector_pedido.buscar_por_id_para_actualizar(pedido_id)
            if pedido is None:
                raise PedidoNoEncontradoError
            if cliente_id is not None and pedido.cliente_id != cliente_id:
                raise PedidoNoPerteneceAClienteError
            pedido.cancelar()
            self._liberar(pedido.detalles)
            self._escritor_pedido.guardar(pedido)
        return pedido

    def _obtener_carrito_del_cliente(
        self, carrito_id: str, cliente_id: str
    ) -> CarritoCompras:
        carrito = self._lector_carrito.buscar_por_id_para_actualizar(carrito_id)
        if carrito is None:
            raise CarritoNoEncontradoError
        if carrito.cliente_id != cliente_id:
            raise CarritoNoPerteneceAClienteError
        return carrito

    @staticmethod
    def _construir_detalles(carrito: CarritoCompras) -> list[DetallePedido]:
        return [
            DetallePedido(
                variante_id=item.variante_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
            )
            for item in carrito.items
        ]

    def _reservar(self, detalles: list[DetallePedido]) -> None:
        self._ajustar_stocks(detalles, lambda stock, cantidad: stock.reservar(cantidad))

    def _liberar(self, detalles: list[DetallePedido]) -> None:
        self._ajustar_stocks(detalles, lambda stock, cantidad: stock.liberar(cantidad))

    def _ajustar_stocks(
        self, detalles: list[DetallePedido], ajuste: AjusteStock
    ) -> None:
        """Bloquea y valida todo, ajusta en memoria y recien entonces persiste.

        Asi una variante inexistente o sin stock suficiente no deja escrituras
        parciales aunque el repositorio no participe de la transaccion.
        """
        if self._inventario is None:
            return
        bloqueados = self._bloquear_stocks(self._inventario, detalles)
        for detalle, stock in bloqueados:
            ajuste(stock, detalle.cantidad)
        for _, stock in bloqueados:
            self._inventario.guardar(stock)

    @staticmethod
    def _bloquear_stocks(
        inventario: RepositorioInventario, detalles: list[DetallePedido]
    ) -> list[tuple[DetallePedido, StockVariante]]:
        """Bloquea por `variante_id` para que reserva y liberacion compartan orden."""
        bloqueados = []
        for detalle in sorted(detalles, key=attrgetter("variante_id")):
            stock = inventario.buscar_por_variante_bloqueada(detalle.variante_id)
            if stock is None:
                raise StockNoEncontradoError(
                    "No existe stock para una variante del pedido"
                )
            bloqueados.append((detalle, stock))
        return bloqueados
