"""Formato uniforme de errores para los modulos de ventas."""

import re

from rest_framework import status
from rest_framework.response import Response

from apps.compartido.presentation.errores import EstadosHttp, estado_http_de


def _codigo_error(error: Exception) -> str:
    nombre = type(error).__name__.removesuffix("Error")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", nombre).lower()


def respuesta_error(error: Exception, estados: EstadosHttp) -> Response:
    return Response(
        {"codigo": _codigo_error(error), "detalle": str(error)},
        status=estado_http_de(error, estados),
    )


def respuesta_entrada_invalida(errores: dict[str, object]) -> Response:
    return Response(
        {"codigo": "entrada_invalida", "detalle": errores},
        status=status.HTTP_400_BAD_REQUEST,
    )
