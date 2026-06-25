"""Controladores Flask para pagos."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import ProcesarPagoDTO
from software_textil.presentation.controllers.http import json_body, optional_str, required_decimal, required_str
from software_textil.presentation.controllers.serializers import to_json

pagos_bp = Blueprint("pagos", __name__, url_prefix="/pagos")


@pagos_bp.post("")
def procesar_pago():
    data = json_body()
    pago = current_app.config["services"]["pagos"].procesar_pago(
        ProcesarPagoDTO(
            pedido_id=required_str(data, "pedido_id"),
            monto=required_decimal(data, "monto"),
            metodo=required_str(data, "metodo"),
            referencia=optional_str(data, "referencia"),
            moneda=optional_str(data, "moneda", "PEN"),
        )
    )
    return jsonify(to_json(pago)), 201
