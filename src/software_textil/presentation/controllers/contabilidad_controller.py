"""Controladores Flask para contabilidad."""

from flask import Blueprint, current_app, jsonify

from software_textil.application.dtos.comandos import RegistrarEgresoDTO, RegistrarIngresoDTO
from software_textil.presentation.controllers.http import json_body, optional_str, required_decimal, required_str
from software_textil.presentation.controllers.serializers import to_json

contabilidad_bp = Blueprint("contabilidad", __name__, url_prefix="/contabilidad")


@contabilidad_bp.post("/ingresos")
def registrar_ingreso():
    data = json_body()
    dto = RegistrarIngresoDTO(
        monto=required_decimal(data, "monto"),
        concepto=required_str(data, "concepto"),
        moneda=optional_str(data, "moneda", "PEN"),
    )
    ingreso = current_app.config["services"]["contabilidad"].registrar_ingreso(dto)
    return jsonify(to_json(ingreso)), 201


@contabilidad_bp.post("/egresos")
def registrar_egreso():
    data = json_body()
    dto = RegistrarEgresoDTO(
        ruc_proveedor=required_str(data, "ruc_proveedor"),
        razon_social=required_str(data, "razon_social"),
        monto=required_decimal(data, "monto"),
        tipo_material=required_str(data, "tipo_material"),
        factura=required_str(data, "factura"),
        contacto=optional_str(data, "contacto"),
        moneda=optional_str(data, "moneda", "PEN"),
    )
    egreso = current_app.config["services"]["contabilidad"].registrar_egreso(dto)
    return jsonify(to_json(egreso)), 201
