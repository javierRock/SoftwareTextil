"""Modelo de reportes operativos y contables."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from software_textil.domain.compartido.enums import FormatoReporte


@dataclass
class Reporte:
    id: str
    tipo: str
    generado_por: str
    formato: FormatoReporte = FormatoReporte.PDF
    fecha_generacion: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReporteInventario(Reporte):
    stock_actual: int = 0
    stock_minimo: int = 0
    movimientos_periodo: int = 0


@dataclass
class ReporteVentas(Reporte):
    total_ventas: Decimal = Decimal("0")
    cantidad_pedidos: int = 0
    periodo_desde: datetime | None = None
    periodo_hasta: datetime | None = None


class ReporteFabrica:
    @staticmethod
    def crear(tipo: str, generado_por: str, formato: FormatoReporte = FormatoReporte.PDF) -> Reporte:
        return Reporte(id=str(uuid4()), tipo=tipo, generado_por=generado_por, formato=formato)
