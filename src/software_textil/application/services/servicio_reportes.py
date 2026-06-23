"""Casos de uso de reportes."""

from uuid import uuid4

from software_textil.domain.compartido.enums import FormatoReporte
from software_textil.domain.reportes.reporte import ReporteInventario
from software_textil.domain.reportes.repositorios import RepositorioReporte


class ServicioReportes:
    def __init__(self, reportes: RepositorioReporte) -> None:
        self.reportes = reportes

    def generar_reporte_inventario(
        self,
        generado_por: str,
        stock_actual: int,
        stock_minimo: int,
        movimientos_periodo: int,
        formato: FormatoReporte = FormatoReporte.PDF,
    ) -> ReporteInventario:
        reporte = ReporteInventario(
            id=str(uuid4()),
            tipo="inventario",
            generado_por=generado_por,
            formato=formato,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo,
            movimientos_periodo=movimientos_periodo,
        )
        self.reportes.guardar(reporte)
        return reporte
