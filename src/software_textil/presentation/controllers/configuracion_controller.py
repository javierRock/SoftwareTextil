"""Controladores Flask para configuracion."""

from flask import Blueprint, current_app, jsonify, request

from software_textil.presentation.controllers.serializers import to_json

configuracion_bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@configuracion_bp.put("/parametros/<clave>")
def actualizar_parametro(clave: str):
    data = request.get_json() or {}
    configuracion = current_app.config["services"]["configuracion"].actualizar_parametro(
        clave,
        data["valor"],
        data["usuario_id"],
    )
    return jsonify(to_json(configuracion))
