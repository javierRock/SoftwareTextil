"""Controladores Flask para usuarios y roles."""

from flask import Blueprint, current_app, jsonify, request

from software_textil.application.dtos.comandos import CrearUsuarioDTO
from software_textil.presentation.controllers.serializers import to_json

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.post("/roles")
def crear_rol():
    data = request.get_json() or {}
    rol = current_app.config["services"]["usuarios"].crear_rol(
        data["nombre"],
        data.get("descripcion", ""),
    )
    return jsonify(to_json(rol)), 201


@usuarios_bp.post("")
def crear_usuario():
    data = request.get_json() or {}
    dto = CrearUsuarioDTO(
        nombre=data["nombre"],
        email=data["email"],
        rol_id=data["rol_id"],
        creado_por=data.get("creado_por"),
    )
    usuario = current_app.config["services"]["usuarios"].crear_usuario(dto)
    return jsonify(to_json(usuario)), 201


@usuarios_bp.post("/<usuario_id>/desactivar")
def desactivar_usuario(usuario_id: str):
    usuario = current_app.config["services"]["usuarios"].desactivar_usuario(usuario_id)
    return jsonify(to_json(usuario))
