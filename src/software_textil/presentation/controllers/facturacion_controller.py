"""Controladores Flask para facturacion electronica."""

from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request

from software_textil.application.dtos.comandos import EmitirComprobanteDTO
from software_textil.presentation.controllers.serializers import to_json

facturacion_bp = Blueprint("facturacion", __name__, url_prefix="/facturacion")


@facturacion_bp.post("/comprobantes")
def emitir_comprobante():
    data = request.get_json() or {}
    dto = EmitirComprobanteDTO(
        serie=data["serie"],
        numero=data["numero"],
        tipo=data.get("tipo", "factura"),
        monto=Decimal(str(data["monto"])),
        igv=Decimal(str(data["igv"])),
        moneda=data.get("moneda", "PEN"),
    )
    comprobante = current_app.config["services"]["facturacion"].emitir_comprobante(dto)
    return jsonify(to_json(comprobante)), 201
