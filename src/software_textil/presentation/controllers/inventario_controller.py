"""Controladores Flask para inventario."""

from flask import Blueprint, current_app, jsonify, request

from software_textil.application.dtos.comandos import AjustarStockDTO, CrearStockDTO, MovimientoStockDTO
from software_textil.presentation.controllers.serializers import to_json

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")


@inventario_bp.post("/stock")
def crear_stock():
    data = request.get_json() or {}
    dto = CrearStockDTO(
        prenda_id=data["prenda_id"],
        stock_inicial=int(data.get("stock_inicial", 0)),
        stock_minimo=int(data.get("stock_minimo", 0)),
        ubicacion=data.get("ubicacion", "almacen"),
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
    data = request.get_json() or {}
    movimiento = current_app.config["services"]["inventario"].registrar_ingreso(_movimiento_dto(data))
    return jsonify(to_json(movimiento)), 201


@inventario_bp.post("/salidas")
def registrar_salida():
    data = request.get_json() or {}
    movimiento = current_app.config["services"]["inventario"].registrar_salida(_movimiento_dto(data))
    return jsonify(to_json(movimiento)), 201


@inventario_bp.post("/ajustes")
def ajustar_stock():
    data = request.get_json() or {}
    dto = AjustarStockDTO(
        prenda_id=data["prenda_id"],
        nueva_cantidad=int(data["nueva_cantidad"]),
        motivo=data["motivo"],
        usuario_id=data["usuario_id"],
    )
    movimiento = current_app.config["services"]["inventario"].ajustar_stock(dto)
    return jsonify(to_json(movimiento)), 201


def _movimiento_dto(data: dict) -> MovimientoStockDTO:
    return MovimientoStockDTO(
        prenda_id=data["prenda_id"],
        cantidad=int(data["cantidad"]),
        motivo=data["motivo"],
        usuario_id=data["usuario_id"],
    )
