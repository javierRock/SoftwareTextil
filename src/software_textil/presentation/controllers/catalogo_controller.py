"""Controladores Flask para catalogo."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import RegistrarPrendaDTO
from software_textil.presentation.controllers.http import json_body, optional_dict, optional_str, required_decimal, required_str
from software_textil.presentation.controllers.serializers import to_json

catalogo_bp = Blueprint("catalogo", __name__, url_prefix="/catalogo")


@catalogo_bp.post("/prendas")
def registrar_prenda():
    data = json_body()
    dto = RegistrarPrendaDTO(
        nombre=required_str(data, "nombre"),
        descripcion=optional_str(data, "descripcion"),
        precio=required_decimal(data, "precio"),
        categoria_id=required_str(data, "categoria_id"),
        registrado_por=required_str(data, "registrado_por"),
        moneda=optional_str(data, "moneda", "PEN"),
        tipo_producto_id=optional_str(data, "tipo_producto_id") or None,
    )
    prenda = current_app.config["services"]["catalogo"].registrar_prenda(dto)
    return jsonify(to_json(prenda)), 201


@catalogo_bp.post("/categorias")
def crear_categoria():
    data = json_body()
    categoria = current_app.config["services"]["catalogo"].crear_categoria(
        required_str(data, "nombre"),
        optional_str(data, "descripcion"),
    )
    return jsonify(to_json(categoria)), 201


@catalogo_bp.post("/tipos-producto")
def crear_tipo_producto():
    data = json_body()
    tipo_producto = current_app.config["services"]["catalogo"].crear_tipo_producto(
        required_str(data, "nombre"),
        optional_dict(data, "atributos_base"),
    )
    return jsonify(to_json(tipo_producto)), 201
