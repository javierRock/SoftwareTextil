"""Traduccion de errores de dominio a respuestas HTTP.

Abierto a extension, cerrado a modificacion (OCP): cada modulo declara su tabla
`{DominioError: codigo HTTP}` y aqui se resuelve el codigo recorriendo la
jerarquia de la excepcion, de la clase mas especifica a la mas general. Agregar
un error nuevo es agregar una fila a esa tabla; ni este resolutor ni las vistas
cambian.
"""

from collections.abc import Mapping

from rest_framework import status
from rest_framework.response import Response

ESTADO_POR_DEFECTO = status.HTTP_400_BAD_REQUEST

EstadosHttp = Mapping[type[Exception], int]


def estado_http_de(
    error: Exception,
    estados: EstadosHttp,
    por_defecto: int = ESTADO_POR_DEFECTO,
) -> int:
    """Devuelve el codigo HTTP registrado para el error o el mas cercano.

    El recorrido usa el MRO de la excepcion, que ya esta ordenado de lo
    especifico a lo general, de modo que un error hijo puede tener su propio
    codigo sin perder el del error base.
    """
    for clase in type(error).__mro__:
        estado = estados.get(clase)
        if estado is not None:
            return estado
    return por_defecto


def respuesta_de_error(
    error: Exception,
    estados: EstadosHttp,
    por_defecto: int = ESTADO_POR_DEFECTO,
) -> Response:
    """Construye la respuesta uniforme de error del API."""
    return Response(
        {"error": str(error)},
        status=estado_http_de(error, estados, por_defecto),
    )
