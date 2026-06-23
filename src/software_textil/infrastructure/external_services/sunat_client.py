"""Adaptador externo para SUNAT."""

from software_textil.domain.facturacion.comprobante import ComprobanteElectronico


class SunatClient:
    def enviar(self, comprobante: ComprobanteElectronico) -> dict[str, str]:
        return {
            "comprobante_id": comprobante.id,
            "estado": "recibido",
            "mensaje": "Comprobante enviado a SUNAT en modo prototipo",
        }
