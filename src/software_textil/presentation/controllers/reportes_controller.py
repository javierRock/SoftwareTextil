"""Controladores Flask para reportes."""

from flask import Blueprint, current_app, jsonify, request

from software_textil.domain.compartido.enums import FormatoReporte
from software_textil.presentation.controllers.serializers import to_json

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@reportes_bp.post("/inventario")
def generar_reporte_inventario():
    data = request.get_json() or {}
    reporte = current_app.config["services"]["reportes"].generar_reporte_inventario(
        generado_por=data["generado_por"],
        stock_actual=int(data.get("stock_actual", 0)),
        stock_minimo=int(data.get("stock_minimo", 0)),
        movimientos_periodo=int(data.get("movimientos_periodo", 0)),
        formato=FormatoReporte(data.get("formato", "pdf")),
    )
    return jsonify(to_json(reporte)), 201
