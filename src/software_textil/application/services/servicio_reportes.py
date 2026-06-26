"""Casos de uso de reportes."""

from uuid import uuid4

from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.compartido.enums import FormatoReporte
from software_textil.domain.reportes.reporte import ReporteInventario
from software_textil.domain.reportes.repositorios import RepositorioReporte


class ServicioReportes:
    def __init__(self, reportes: RepositorioReporte, unit_of_work: UnitOfWork | None = None) -> None:
        self.reportes = reportes
        self.uow = unit_of_work or NoOpUnitOfWork()

    def generar_reporte_inventario(
        self,
        generado_por: str,
        stock_actual: int,
        stock_minimo: int,
        movimientos_periodo: int,
        formato: FormatoReporte = FormatoReporte.PDF,
    ) -> ReporteInventario:
        with self.uow:
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
            self.uow.commit()
        return reporte
