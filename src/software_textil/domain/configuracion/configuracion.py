"""Configuracion general y parametros del sistema."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class ParametroSistema:
    id: str
    clave: str
    valor: str
    tipo: str
    descripcion: str = ""


@dataclass
class ConfiguracionGeneral:
    id: str
    modificado_por: str | None = None
    ultima_modificacion: datetime = field(default_factory=datetime.utcnow)
    parametros: dict[str, ParametroSistema] = field(default_factory=dict)

    def actualizar_parametro(self, clave: str, valor: str, usuario_id: str) -> None:
        if clave not in self.parametros:
            raise ValueError("El parametro no existe")
        self.parametros[clave].valor = valor
        self.modificado_por = usuario_id
        self.ultima_modificacion = datetime.utcnow()


class ConfiguracionFabrica:
    @staticmethod
    def crear_default() -> ConfiguracionGeneral:
        return ConfiguracionGeneral(id=str(uuid4()))
