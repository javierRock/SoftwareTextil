"""Controladores Flask para usuarios y roles."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import CrearUsuarioDTO
from software_textil.presentation.controllers.http import json_body, optional_str, required_str
from software_textil.presentation.controllers.serializers import to_json

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.post("/roles")
def crear_rol():
    data = json_body()
    rol = current_app.config["services"]["usuarios"].crear_rol(
        required_str(data, "nombre"),
        optional_str(data, "descripcion"),
    )
    return jsonify(to_json(rol)), 201


@usuarios_bp.post("")
def crear_usuario():
    data = json_body()
    dto = CrearUsuarioDTO(
        nombre=required_str(data, "nombre"),
        email=required_str(data, "email"),
        rol_id=required_str(data, "rol_id"),
        creado_por=optional_str(data, "creado_por") or None,
        password=optional_str(data, "password") or None,
        username=optional_str(data, "username") or None,
    )
    usuario = current_app.config["services"]["usuarios"].crear_usuario(dto)
    return jsonify(to_json(usuario)), 201


@usuarios_bp.post("/<usuario_id>/desactivar")
def desactivar_usuario(usuario_id: str):
    usuario = current_app.config["services"]["usuarios"].desactivar_usuario(usuario_id)
    return jsonify(to_json(usuario))
