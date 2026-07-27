"""Servicios de aplicacion para despachos."""

from apps.ventas.despachos.domain.despacho import (
    Despacho,
    DespachoFabrica,
    GuiaRemision,
)
from apps.ventas.despachos.domain.errors import DespachoNoEncontradoError
from apps.ventas.despachos.domain.repositorios import RepositorioDespacho


class ServicioDespachos:
    """Coordina la preparacion, confirmacion y cancelacion de despachos."""

    def __init__(self, repo_despachos: RepositorioDespacho) -> None:
        self.repo_despachos = repo_despachos

    def programar(self, pedido_id: str, direccion_entrega: str) -> Despacho:
        despacho = DespachoFabrica.crear(pedido_id, direccion_entrega)
        self.repo_despachos.guardar(despacho)
        return despacho

    def preparar(self, despacho_id: str, responsable_id: str) -> Despacho:
        despacho = self._obtener(despacho_id)
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
        despacho = self._obtener(despacho_id)
        despacho.confirmar(GuiaRemision(serie, numero, transportista))
        self.repo_despachos.guardar(despacho)
        return despacho

    def cancelar(self, despacho_id: str) -> Despacho:
        despacho = self._obtener(despacho_id)
        despacho.cancelar()
        self.repo_despachos.guardar(despacho)
        return despacho

    def consultar(self, despacho_id: str) -> Despacho:
        return self._obtener(despacho_id)

    def listar(self) -> list[Despacho]:
        return self.repo_despachos.listar()

    def _obtener(self, despacho_id: str) -> Despacho:
        despacho = self.repo_despachos.buscar_por_id(despacho_id)
        if despacho is None:
            raise DespachoNoEncontradoError
        return despacho
