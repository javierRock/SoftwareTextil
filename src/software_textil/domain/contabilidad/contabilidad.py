"""Entidades contables refinadas desde sistemaContableTextil."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.periodo import Periodo


@dataclass
class Proveedor:
    ruc: str
    razon_social: str
    contacto: str = ""


@dataclass
class Ingreso:
    id: str
    monto: Dinero
    fecha: datetime
    concepto: str


@dataclass
class EgresoTextil:
    id: str
    proveedor: Proveedor
    monto: Dinero
    tipo_material: str
    factura: str


@dataclass
class PeriodoContable:
    periodo: Periodo
    estado: str = "abierto"
    cerrado_por: str | None = None
    fecha_cierre: datetime | None = None

    def cerrar(self, usuario_id: str) -> None:
        if self.estado == "cerrado":
            raise ValueError("El periodo ya esta cerrado")
        self.estado = "cerrado"
        self.cerrado_por = usuario_id
        self.fecha_cierre = datetime.utcnow()

    def reabrir(self) -> None:
        self.estado = "abierto"
        self.cerrado_por = None
        self.fecha_cierre = None


@dataclass
class LibroRegistro:
    periodo: Periodo
    tipo_libro: str
    total_igv: Dinero
    total_iva: Dinero
    lineas: list[str] = field(default_factory=list)


class MovimientoContableFabrica:
    @staticmethod
    def crear_ingreso(monto: Dinero, concepto: str) -> Ingreso:
        return Ingreso(id=str(uuid4()), monto=monto, fecha=datetime.utcnow(), concepto=concepto)

    @staticmethod
    def crear_egreso(proveedor: Proveedor, monto: Dinero, tipo_material: str, factura: str) -> EgresoTextil:
        return EgresoTextil(
            id=str(uuid4()),
            proveedor=proveedor,
            monto=monto,
            tipo_material=tipo_material,
            factura=factura,
        )
