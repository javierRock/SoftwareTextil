"""Datos de auditoria compartidos entre agregados."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DatosAuditoria:
    creado_en: datetime
    creado_por: str
    modificado_en: datetime | None = None
    modificado_por: str | None = None
