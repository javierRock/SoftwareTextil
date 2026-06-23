"""Registro de auditoria transversal."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class RegistroAuditoria:
    id: str
    entidad_id: str
    entidad: str
    accion: str
    realizado_por: str
    detalles: str
    ip: str
    fecha: datetime = field(default_factory=datetime.utcnow)


class AuditoriaFabrica:
    @staticmethod
    def crear(entidad_id: str, entidad: str, accion: str, usuario_id: str, detalles: str, ip: str) -> RegistroAuditoria:
        return RegistroAuditoria(
            id=str(uuid4()),
            entidad_id=entidad_id,
            entidad=entidad,
            accion=accion,
            realizado_por=usuario_id,
            detalles=detalles,
            ip=ip,
        )
