"""Casos de uso contables."""

from software_textil.application.dtos.comandos import RegistrarEgresoDTO, RegistrarIngresoDTO
from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.contabilidad.contabilidad import EgresoTextil, Ingreso, MovimientoContableFabrica, PeriodoContable, Proveedor
from software_textil.domain.contabilidad.repositorios import RepositorioEgreso, RepositorioIngreso, RepositorioPeriodoContable


class ServicioContabilidad:
    def __init__(
        self,
        ingresos: RepositorioIngreso,
        egresos: RepositorioEgreso,
        periodos: RepositorioPeriodoContable,
    ) -> None:
        self.ingresos = ingresos
        self.egresos = egresos
        self.periodos = periodos

    def registrar_ingreso(self, dto: RegistrarIngresoDTO) -> Ingreso:
        ingreso = MovimientoContableFabrica.crear_ingreso(Dinero(dto.monto, dto.moneda), dto.concepto)
        self.ingresos.guardar(ingreso)
        return ingreso

    def registrar_egreso(self, dto: RegistrarEgresoDTO) -> EgresoTextil:
        proveedor = Proveedor(dto.ruc_proveedor, dto.razon_social, dto.contacto)
        egreso = MovimientoContableFabrica.crear_egreso(
            proveedor,
            Dinero(dto.monto, dto.moneda),
            dto.tipo_material,
            dto.factura,
        )
        self.egresos.guardar(egreso)
        return egreso

    def cerrar_periodo(self, periodo: PeriodoContable, usuario_id: str) -> PeriodoContable:
        periodo.cerrar(usuario_id)
        self.periodos.guardar(periodo)
        return periodo
