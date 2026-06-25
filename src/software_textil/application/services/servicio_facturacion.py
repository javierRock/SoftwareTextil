"""Casos de uso de facturacion electronica."""

from software_textil.application.dtos.comandos import EmitirComprobanteDTO
from software_textil.application.errors import ExternalServiceError
from software_textil.application.ports import SunatPort
from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import TipoComprobante
from software_textil.domain.facturacion.comprobante import ComprobanteElectronico, ComprobanteFactory


class ServicioFacturacion:
    def __init__(self, sunat_client: SunatPort) -> None:
        self.sunat_client = sunat_client

    def emitir_comprobante(self, dto: EmitirComprobanteDTO) -> ComprobanteElectronico:
        monto = Dinero(dto.monto, dto.moneda)
        igv = Dinero(dto.igv, dto.moneda)
        tipo = TipoComprobante(dto.tipo)
        if tipo == TipoComprobante.FACTURA:
            comprobante = ComprobanteFactory.crear_factura(dto.serie, dto.numero, monto, igv)
        else:
            comprobante = ComprobanteFactory.crear_boleta(dto.serie, dto.numero, monto, igv)

        try:
            self.sunat_client.enviar(comprobante)
        except Exception as exc:
            raise ExternalServiceError("No se pudo enviar el comprobante a SUNAT") from exc
        comprobante.marcar_enviado()
        return comprobante
