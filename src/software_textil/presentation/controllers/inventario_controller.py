"""Controladores Flask para inventario."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import AjustarStockDTO, CrearStockDTO, MovimientoStockDTO
from software_textil.presentation.controllers.http import json_body, optional_str, required_int, required_str
from software_textil.presentation.controllers.serializers import to_json

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@inventario_bp.post("/stock")
def crear_stock():
    data = json_body()
    dto = CrearStockDTO(
        prenda_id=required_str(data, "prenda_id"),
        stock_inicial=required_int(data, "stock_inicial"),
        stock_minimo=required_int(data, "stock_minimo"),
        ubicacion=optional_str(data, "ubicacion", "almacen"),
    )
    stock = current_app.config["services"]["inventario"].crear_stock(dto)
    return jsonify(to_json(stock)), 201


@inventario_bp.get("/stock/<prenda_id>")
def consultar_stock(prenda_id: str):
    stock = current_app.config["services"]["inventario"].consultar_stock(prenda_id)
    if stock is None:
        return jsonify({"error": "stock no encontrado"}), 404
    return jsonify(to_json(stock))


@inventario_bp.post("/ingresos")
def registrar_ingreso():
    data = json_body()
    movimiento = current_app.config["services"]["inventario"].registrar_ingreso(_movimiento_dto(data))
    return jsonify(to_json(movimiento)), 201


@inventario_bp.post("/salidas")
def registrar_salida():
    data = json_body()
    movimiento = current_app.config["services"]["inventario"].registrar_salida(_movimiento_dto(data))
    return jsonify(to_json(movimiento)), 201


@inventario_bp.post("/ajustes")
def ajustar_stock():
    data = json_body()
    dto = AjustarStockDTO(
        prenda_id=required_str(data, "prenda_id"),
        nueva_cantidad=required_int(data, "nueva_cantidad"),
        motivo=required_str(data, "motivo"),
        usuario_id=required_str(data, "usuario_id"),
    )
    movimiento = current_app.config["services"]["inventario"].ajustar_stock(dto)
    return jsonify(to_json(movimiento)), 201


def _movimiento_dto(data: dict) -> MovimientoStockDTO:
    return MovimientoStockDTO(
        prenda_id=required_str(data, "prenda_id"),
        cantidad=required_int(data, "cantidad"),
        motivo=required_str(data, "motivo"),
        usuario_id=required_str(data, "usuario_id"),
    )
