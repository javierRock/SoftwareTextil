"""Utilidades pequenas para validar entradas HTTP."""

from decimal import Decimal, InvalidOperation
from typing import Any

from flask import request

from software_textil.application.errors import ValidationError


def json_body() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationError("El cuerpo JSON debe ser un objeto")
    return data


def required_str(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Campo requerido: {field}")
    return value.strip()


def optional_str(data: dict[str, Any], field: str, default: str = "") -> str:
    value = data.get(field, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise ValidationError(f"El campo {field} debe ser texto")
    return value.strip()


def required_int(data: dict[str, Any], field: str) -> int:
    if field not in data:
        raise ValidationError(f"Campo requerido: {field}")
    try:
        return int(data[field])
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"El campo {field} debe ser entero") from exc


def optional_int(data: dict[str, Any], field: str, default: int = 0) -> int:
    if field not in data or data[field] is None:
        return default
    try:
        return int(data[field])
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"El campo {field} debe ser entero") from exc


def required_decimal(data: dict[str, Any], field: str) -> Decimal:
    if field not in data:
        raise ValidationError(f"Campo requerido: {field}")
    try:
        return Decimal(str(data[field]))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"El campo {field} debe ser decimal") from exc


def optional_dict(data: dict[str, Any], field: str) -> dict[str, str]:
    value = data.get(field, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError(f"El campo {field} debe ser un objeto")
    return {str(key): str(item) for key, item in value.items()}


def optional_str_list(data: dict[str, Any], field: str) -> list[str]:
    value = data.get(field, [])
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValidationError(f"El campo {field} debe ser una lista de textos")
    return value
