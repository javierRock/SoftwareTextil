"""Controladores Flask para configuracion."""

from flask import Blueprint, current_app, jsonify

from software_textil.presentation.controllers.http import json_body, required_str
from software_textil.presentation.controllers.serializers import to_json

configuracion_bp = Blueprint("configuracion", __name__, url_prefix="/configuracion")


@configuracion_bp.put("/parametros/<clave>")
def actualizar_parametro(clave: str):
    data = json_body()
    configuracion = current_app.config["services"]["configuracion"].actualizar_parametro(
        clave,
        required_str(data, "valor"),
        required_str(data, "usuario_id"),
    )
    return jsonify(to_json(configuracion))
