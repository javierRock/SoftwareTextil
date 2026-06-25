"""Controladores Flask para despachos."""

from flask import Blueprint, current_app, jsonify

from software_textil.presentation.controllers.http import json_body, optional_str_list, required_str
from software_textil.presentation.controllers.serializers import to_json

despachos_bp = Blueprint("despachos", __name__, url_prefix="/despachos")


@despachos_bp.post("")
def crear_despacho():
    data = json_body()
    despacho = current_app.config["services"]["despachos"].crear_despacho(
        required_str(data, "cliente"),
        optional_str_list(data, "movimientos_ids"),
    )
    return jsonify(to_json(despacho)), 201


@despachos_bp.post("/<despacho_id>/preparar")
def preparar_despacho(despacho_id: str):
    despacho = current_app.config["services"]["despachos"].preparar(despacho_id)
    return jsonify(to_json(despacho))


@despachos_bp.post("/<despacho_id>/confirmar")
def confirmar_despacho(despacho_id: str):
    despacho = current_app.config["services"]["despachos"].confirmar(despacho_id)
    return jsonify(to_json(despacho))


@despachos_bp.post("/<despacho_id>/cancelar")
def cancelar_despacho(despacho_id: str):
    despacho = current_app.config["services"]["despachos"].cancelar(despacho_id)
    return jsonify(to_json(despacho))
