"""Casos de uso de despachos."""

from software_textil.application.errors import NotFoundError
from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.despachos.despacho import Despacho, FabricaDespacho
from software_textil.domain.despachos.repositorios import RepositorioDespacho


class ServicioDespachos:
    def __init__(self, despachos: RepositorioDespacho, unit_of_work: UnitOfWork | None = None) -> None:
        self.despachos = despachos
        self.uow = unit_of_work or NoOpUnitOfWork()

    def crear_despacho(self, cliente: str, movimientos_ids: list[str] | None = None) -> Despacho:
        with self.uow:
            despacho = FabricaDespacho.crear(cliente, movimientos_ids)
            self.despachos.guardar(despacho)
            self.uow.commit()
        return despacho

    def preparar(self, despacho_id: str) -> Despacho:
        with self.uow:
            despacho = self._obtener(despacho_id)
            despacho.preparar()
            self.despachos.guardar(despacho)
            self.uow.commit()
        return despacho

    def confirmar(self, despacho_id: str) -> Despacho:
        with self.uow:
            despacho = self._obtener(despacho_id)
            despacho.confirmar()
            self.despachos.guardar(despacho)
            self.uow.commit()
        return despacho

    def cancelar(self, despacho_id: str) -> Despacho:
        with self.uow:
            despacho = self._obtener(despacho_id)
            despacho.cancelar()
            self.despachos.guardar(despacho)
            self.uow.commit()
        return despacho

    def _obtener(self, despacho_id: str) -> Despacho:
        despacho = self.despachos.buscar_por_id(despacho_id)
        if despacho is None:
            raise NotFoundError("El despacho no existe")
        return despacho
