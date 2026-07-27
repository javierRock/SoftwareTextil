"""Servicios de aplicacion para despachos."""

from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext

from django.db import IntegrityError

from apps.compartido.domain.enums import EstadoPedido
from apps.inventario.domain.excepciones import StockNoEncontradoError
from apps.inventario.domain.repositorios import (
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from apps.ventas.despachos.domain.despacho import (
    Despacho,
    DespachoFabrica,
    GuiaRemision,
)
from apps.ventas.despachos.domain.errors import (
    DespachoNoEncontradoError,
    DespachoYaExisteError,
    GuiaRemisionDuplicadaError,
    PedidoDespachoNoEncontradoError,
    PedidoNoPagadoError,
)
from apps.ventas.despachos.domain.repositorios import RepositorioDespacho
from apps.ventas.pedidos.domain.repositorios import LectorPedido


class ServicioDespachos:
    """Coordina la preparacion, confirmacion y cancelacion de despachos."""

    def __init__(
        self,
        repo_despachos: RepositorioDespacho,
        repo_pedidos: LectorPedido | None = None,
        unidad_trabajo: Callable[[], AbstractContextManager] = nullcontext,
        inventario: RepositorioInventario | None = None,
        movimientos: RepositorioMovimientoInventario | None = None,
    ) -> None:
        self.repo_despachos = repo_despachos
        self.repo_pedidos = repo_pedidos
        self.unidad_trabajo = unidad_trabajo
        self.inventario = inventario
        self.movimientos = movimientos

    def programar(self, pedido_id: str, direccion_entrega: str) -> Despacho:
        with self.unidad_trabajo():
            if self.repo_pedidos is not None:
                pedido = self.repo_pedidos.buscar_por_id_para_actualizar(pedido_id)
                if pedido is None:
                    raise PedidoDespachoNoEncontradoError
                if pedido.estado != EstadoPedido.PAGADO:
                    raise PedidoNoPagadoError
            if self.repo_despachos.buscar_por_pedido(pedido_id) is not None:
                raise DespachoYaExisteError
            despacho = DespachoFabrica.crear(pedido_id, direccion_entrega)
            try:
                self.repo_despachos.guardar(despacho)
            except IntegrityError as error:
                raise DespachoYaExisteError from error
        return despacho

    def preparar(self, despacho_id: str, responsable_id: str) -> Despacho:
        with self.unidad_trabajo():
            despacho = self._obtener(despacho_id, para_actualizar=True)
            despacho.preparar(responsable_id)
            self.repo_despachos.guardar(despacho)
        return despacho

    def confirmar(
        self,
        despacho_id: str,
        serie: str,
        numero: str,
        transportista: str = "",
    ) -> Despacho:
        with self.unidad_trabajo():
            despacho = self._obtener(despacho_id, para_actualizar=True)
            despacho.confirmar(GuiaRemision(serie, numero, transportista))
            self._descontar_reservas(despacho)
            try:
                self.repo_despachos.guardar(despacho)
            except IntegrityError as error:
                raise GuiaRemisionDuplicadaError from error
        return despacho

    def _descontar_reservas(self, despacho: Despacho) -> None:
        if (
            self.repo_pedidos is None
            or self.inventario is None
            or self.movimientos is None
        ):
            return
        pedido = self.repo_pedidos.buscar_por_id_para_actualizar(despacho.pedido_id)
        if pedido is None:
            raise PedidoDespachoNoEncontradoError
        for detalle in sorted(pedido.detalles, key=lambda item: item.variante_id):
            stock = self.inventario.buscar_por_variante_bloqueada(
                detalle.variante_id
            )
            if stock is None:
                raise StockNoEncontradoError(
                    "No existe stock para una variante del despacho"
                )
            movimiento = stock.despachar_reserva(
                detalle.cantidad,
                f"Despacho del pedido {pedido.id}",
                despacho.responsable_id,
            )
            self.inventario.guardar(stock)
            self.movimientos.guardar(movimiento)

    def cancelar(self, despacho_id: str) -> Despacho:
        with self.unidad_trabajo():
            despacho = self._obtener(despacho_id, para_actualizar=True)
            despacho.cancelar()
            self.repo_despachos.guardar(despacho)
        return despacho

    def consultar(self, despacho_id: str) -> Despacho:
        return self._obtener(despacho_id)

    def listar(self) -> list[Despacho]:
        return self.repo_despachos.listar()

    def _obtener(
        self, despacho_id: str, para_actualizar: bool = False
    ) -> Despacho:
        buscador = (
            self.repo_despachos.buscar_por_id_para_actualizar
            if para_actualizar
            else self.repo_despachos.buscar_por_id
        )
        despacho = buscador(despacho_id)
        if despacho is None:
            raise DespachoNoEncontradoError
        return despacho
