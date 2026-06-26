"""Contratos de configuracion."""

from abc import ABC, abstractmethod

from software_textil.domain.configuracion.configuracion import ConfiguracionGeneral


class RepositorioConfiguracion(ABC):
    @abstractmethod
    def guardar(self, configuracion: ConfiguracionGeneral) -> None:
        raise NotImplementedError

    @abstractmethod
    def obtener(self) -> ConfiguracionGeneral | None:
        raise NotImplementedError
