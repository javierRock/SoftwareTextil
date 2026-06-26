"""Controladores Flask para pedidos."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import CrearPedidoDTO
from software_textil.presentation.controllers.http import json_body, required_str
from software_textil.presentation.controllers.serializers import to_json

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


@pedidos_bp.post("")
def generar_pedido():
    data = json_body()
    pedido = current_app.config["services"]["pedidos"].generar_desde_carrito(
        CrearPedidoDTO(
            carrito_id=required_str(data, "carrito_id"),
            cliente_id=required_str(data, "cliente_id"),
        )
    )
    return jsonify(to_json(pedido)), 201


@pedidos_bp.get("/<pedido_id>")
def obtener_pedido(pedido_id: str):
    pedido = current_app.config["services"]["pedidos"].obtener_pedido(pedido_id)
    return jsonify(to_json(pedido))


@pedidos_bp.post("/<pedido_id>/cancelar")
def cancelar_pedido(pedido_id: str):
    pedido = current_app.config["services"]["pedidos"].cancelar(pedido_id)
    return jsonify(to_json(pedido))
