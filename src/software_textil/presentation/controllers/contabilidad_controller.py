"""Controladores Flask para contabilidad."""

from decimal import Decimal

from flask import Blueprint, current_app, jsonify, request

from software_textil.application.dtos.comandos import RegistrarEgresoDTO, RegistrarIngresoDTO
from software_textil.presentation.controllers.serializers import to_json

contabilidad_bp = Blueprint("contabilidad", __name__, url_prefix="/contabilidad")


@contabilidad_bp.post("/ingresos")
def registrar_ingreso():
    data = request.get_json() or {}
    dto = RegistrarIngresoDTO(
        monto=Decimal(str(data["monto"])),
        concepto=data["concepto"],
        moneda=data.get("moneda", "PEN"),
    )
    ingreso = current_app.config["services"]["contabilidad"].registrar_ingreso(dto)
    return jsonify(to_json(ingreso)), 201


@contabilidad_bp.post("/egresos")
def registrar_egreso():
    data = request.get_json() or {}
    dto = RegistrarEgresoDTO(
        ruc_proveedor=data["ruc_proveedor"],
        razon_social=data["razon_social"],
        monto=Decimal(str(data["monto"])),
        tipo_material=data["tipo_material"],
        factura=data["factura"],
        contacto=data.get("contacto", ""),
        moneda=data.get("moneda", "PEN"),
    )
    egreso = current_app.config["services"]["contabilidad"].registrar_egreso(dto)
    return jsonify(to_json(egreso)), 201
