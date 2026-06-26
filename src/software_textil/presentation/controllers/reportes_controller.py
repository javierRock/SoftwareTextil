"""Controladores Flask para reportes."""

from flask import Blueprint, current_app, jsonify

from software_textil.domain.compartido.enums import FormatoReporte
from software_textil.presentation.controllers.http import json_body, optional_int, optional_str, required_str
from software_textil.presentation.controllers.serializers import to_json

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@reportes_bp.post("/inventario")
def generar_reporte_inventario():
    data = json_body()
    reporte = current_app.config["services"]["reportes"].generar_reporte_inventario(
        generado_por=required_str(data, "generado_por"),
        stock_actual=optional_int(data, "stock_actual"),
        stock_minimo=optional_int(data, "stock_minimo"),
        movimientos_periodo=optional_int(data, "movimientos_periodo"),
        formato=FormatoReporte(optional_str(data, "formato", "pdf")),
    )
    return jsonify(to_json(reporte)), 201
