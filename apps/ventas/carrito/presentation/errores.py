"""Codigos HTTP de los errores del dominio de carrito.

Punto de extension (OCP): para que un error nuevo devuelva otro codigo basta
con agregar su fila a `ESTADOS_HTTP`; las vistas no se modifican.
"""

from rest_framework import status
from rest_framework.response import Response

from apps.compartido.presentation.errores import EstadosHttp, respuesta_de_error
from apps.ventas.carrito.domain.errors import CarritoError, CarritoNoEncontradoError

ESTADOS_HTTP: EstadosHttp = {
    CarritoNoEncontradoError: status.HTTP_404_NOT_FOUND,
    CarritoError: status.HTTP_400_BAD_REQUEST,
}


def respuesta_de_error_carrito(error: CarritoError) -> Response:
    return respuesta_de_error(error, ESTADOS_HTTP)
