"""Controladores Flask para catalogo."""

from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request

from software_textil.application.dtos.comandos import RegistrarPrendaDTO
from software_textil.presentation.controllers.serializers import to_json

catalogo_bp = Blueprint("catalogo", __name__, url_prefix="/catalogo")


@catalogo_bp.post("/prendas")
def registrar_prenda():
    data = request.get_json() or {}
    dto = RegistrarPrendaDTO(
        nombre=data["nombre"],
        descripcion=data.get("descripcion", ""),
        precio=Decimal(str(data["precio"])),
        categoria_id=data["categoria_id"],
        registrado_por=data["registrado_por"],
        moneda=data.get("moneda", "PEN"),
        tipo_producto_id=data.get("tipo_producto_id"),
    )
    prenda = current_app.config["services"]["catalogo"].registrar_prenda(dto)
    return jsonify(to_json(prenda)), 201


@catalogo_bp.post("/categorias")
def crear_categoria():
    data = request.get_json() or {}
    categoria = current_app.config["services"]["catalogo"].crear_categoria(
        data["nombre"],
        data.get("descripcion", ""),
    )
    return jsonify(to_json(categoria)), 201


@catalogo_bp.post("/tipos-producto")
def crear_tipo_producto():
    data = request.get_json() or {}
    tipo_producto = current_app.config["services"]["catalogo"].crear_tipo_producto(
        data["nombre"],
        data.get("atributos_base", {}),
    )
    return jsonify(to_json(tipo_producto)), 201
