"""Casos de uso de configuracion."""

from software_textil.domain.configuracion.configuracion import ConfiguracionGeneral
from software_textil.domain.configuracion.repositorios import RepositorioConfiguracion


class ServicioConfiguracion:
    def __init__(self, configuraciones: RepositorioConfiguracion) -> None:
        self.configuraciones = configuraciones

    def actualizar_parametro(self, clave: str, valor: str, usuario_id: str) -> ConfiguracionGeneral:
        configuracion = self.configuraciones.obtener()
        if configuracion is None:
            raise ValueError("No existe configuracion general")
        configuracion.actualizar_parametro(clave, valor, usuario_id)
        self.configuraciones.guardar(configuracion)
        return configuracion
