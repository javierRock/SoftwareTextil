"""Comprobantes electronicos SUNAT."""

from dataclasses import dataclass
from uuid import uuid4

from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import TipoComprobante


@dataclass
class ComprobanteElectronico:
    id: str
    serie: str
    numero: str
    tipo: TipoComprobante
    estado_sunat: str
    monto: Dinero
    igv: Dinero

    def marcar_enviado(self) -> None:
        self.estado_sunat = "enviado"

    def marcar_aceptado(self) -> None:
        self.estado_sunat = "aceptado"


class ComprobanteFactory:
    @staticmethod
    def crear_factura(serie: str, numero: str, monto: Dinero, igv: Dinero) -> ComprobanteElectronico:
        return ComprobanteElectronico(
            id=str(uuid4()),
            serie=serie,
            numero=numero,
            tipo=TipoComprobante.FACTURA,
            estado_sunat="pendiente",
            monto=monto,
            igv=igv,
        )

    @staticmethod
    def crear_boleta(serie: str, numero: str, monto: Dinero, igv: Dinero) -> ComprobanteElectronico:
        return ComprobanteElectronico(
            id=str(uuid4()),
            serie=serie,
            numero=numero,
            tipo=TipoComprobante.BOLETA,
            estado_sunat="pendiente",
            monto=monto,
            igv=igv,
        )
