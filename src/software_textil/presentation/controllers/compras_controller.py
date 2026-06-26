"""Controladores Flask para compras y carrito."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import ActualizarItemCarritoDTO, AgregarItemCarritoDTO, CrearCarritoDTO
from software_textil.presentation.controllers.http import json_body, optional_str, required_decimal, required_int, required_str
from software_textil.presentation.controllers.serializers import to_json

compras_bp = Blueprint("compras", __name__, url_prefix="/compras")


@compras_bp.post("/carritos")
def crear_carrito():
    data = json_body()
    carrito = current_app.config["services"]["compras"].crear_carrito(
        CrearCarritoDTO(cliente_id=required_str(data, "cliente_id"))
    )
    return jsonify(to_json(carrito)), 201


@compras_bp.get("/carritos/<carrito_id>")
def obtener_carrito(carrito_id: str):
    carrito = current_app.config["services"]["compras"].obtener_carrito(carrito_id)
    return jsonify(to_json(carrito))


@compras_bp.post("/carritos/<carrito_id>/items")
def agregar_item(carrito_id: str):
    data = json_body()
    carrito = current_app.config["services"]["compras"].agregar_item(
        AgregarItemCarritoDTO(
            carrito_id=carrito_id,
            prenda_id=required_str(data, "prenda_id"),
            cantidad=required_int(data, "cantidad"),
            precio_unitario=required_decimal(data, "precio_unitario"),
            moneda=optional_str(data, "moneda", "PEN"),
        )
    )
    return jsonify(to_json(carrito)), 201


@compras_bp.put("/carritos/<carrito_id>/items/<prenda_id>")
def actualizar_item(carrito_id: str, prenda_id: str):
    data = json_body()
    carrito = current_app.config["services"]["compras"].actualizar_item(
        ActualizarItemCarritoDTO(
            carrito_id=carrito_id,
            prenda_id=prenda_id,
            cantidad=required_int(data, "cantidad"),
        )
    )
    return jsonify(to_json(carrito))


@compras_bp.delete("/carritos/<carrito_id>/items/<prenda_id>")
def quitar_item(carrito_id: str, prenda_id: str):
    carrito = current_app.config["services"]["compras"].quitar_item(carrito_id, prenda_id)
    return jsonify(to_json(carrito))
