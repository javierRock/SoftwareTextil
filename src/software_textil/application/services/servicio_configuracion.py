"""Casos de uso de configuracion."""

from software_textil.application.errors import NotFoundError
from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.configuracion.configuracion import ConfiguracionGeneral
from software_textil.domain.configuracion.repositorios import RepositorioConfiguracion


class ServicioConfiguracion:
    def __init__(self, configuraciones: RepositorioConfiguracion, unit_of_work: UnitOfWork | None = None) -> None:
        self.configuraciones = configuraciones
        self.uow = unit_of_work or NoOpUnitOfWork()

    def actualizar_parametro(self, clave: str, valor: str, usuario_id: str) -> ConfiguracionGeneral:
        configuracion = self.configuraciones.obtener()
        if configuracion is None:
            raise NotFoundError("No existe configuracion general")
        with self.uow:
            configuracion.actualizar_parametro(clave, valor, usuario_id)
            self.configuraciones.guardar(configuracion)
            self.uow.commit()
        return configuracion
