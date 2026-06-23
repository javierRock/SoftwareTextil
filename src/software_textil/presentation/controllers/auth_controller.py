"""Controladores Flask para autenticacion."""

from flask import Blueprint, current_app, jsonify, request

from software_textil.application.dtos.comandos import LoginDTO
from software_textil.presentation.controllers.serializers import to_json

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    dto = LoginDTO(
        username=data["username"],
        password=data["password"],
        ip=request.remote_addr or data.get("ip", ""),
    )
    resultado, sesion = current_app.config["services"]["autenticacion"].autenticar(dto)
    return jsonify({"resultado": resultado.value, "sesion": to_json(sesion)})


@auth_bp.post("/logout")
def logout():
    data = request.get_json() or {}
    current_app.config["services"]["autenticacion"].cerrar_sesion(data["token"])
    return jsonify({"status": "ok"})
