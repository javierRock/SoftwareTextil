"""Controladores Flask para facturacion electronica."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import EmitirComprobanteDTO
from software_textil.presentation.controllers.http import json_body, optional_str, required_decimal, required_str
from software_textil.presentation.controllers.serializers import to_json

facturacion_bp = Blueprint("facturacion", __name__, url_prefix="/facturacion")


@facturacion_bp.post("/comprobantes")
def emitir_comprobante():
    data = json_body()
    dto = EmitirComprobanteDTO(
        serie=required_str(data, "serie"),
        numero=required_str(data, "numero"),
        tipo=optional_str(data, "tipo", "factura"),
        monto=required_decimal(data, "monto"),
        igv=required_decimal(data, "igv"),
        moneda=optional_str(data, "moneda", "PEN"),
    )
    comprobante = current_app.config["services"]["facturacion"].emitir_comprobante(dto)
    return jsonify(to_json(comprobante)), 201
