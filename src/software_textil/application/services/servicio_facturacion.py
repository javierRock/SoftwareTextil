"""Casos de uso de facturacion electronica."""

from software_textil.application.dtos.comandos import EmitirComprobanteDTO
from software_textil.domain.compartido.dinero import Dinero
from software_textil.domain.compartido.enums import TipoComprobante
from software_textil.domain.facturacion.comprobante import ComprobanteElectronico, ComprobanteFactory


class ServicioFacturacion:
    def __init__(self, sunat_client: object) -> None:
        self.sunat_client = sunat_client

    def emitir_comprobante(self, dto: EmitirComprobanteDTO) -> ComprobanteElectronico:
        monto = Dinero(dto.monto, dto.moneda)
        igv = Dinero(dto.igv, dto.moneda)
        if dto.tipo == TipoComprobante.FACTURA:
            comprobante = ComprobanteFactory.crear_factura(dto.serie, dto.numero, monto, igv)
        else:
            comprobante = ComprobanteFactory.crear_boleta(dto.serie, dto.numero, monto, igv)

        enviar = getattr(self.sunat_client, "enviar", None)
        if callable(enviar):
            enviar(comprobante)
            comprobante.marcar_enviado()
        return comprobante
