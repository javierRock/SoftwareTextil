"""Codigos HTTP de los errores del dominio de despachos.

Punto de extension (OCP): para que un error nuevo devuelva otro codigo basta
con agregar su fila a `ESTADOS_HTTP`; las vistas no se modifican.
"""

from rest_framework import status
from rest_framework.response import Response

from apps.compartido.domain.errors import DominioError
from apps.compartido.presentation.errores import EstadosHttp, respuesta_de_error
from apps.ventas.despachos.domain.errors import (
    DespachoConfirmadoError,
    DespachoNoEncontradoError,
)

ESTADOS_HTTP: EstadosHttp = {
    DespachoNoEncontradoError: status.HTTP_404_NOT_FOUND,
    DespachoConfirmadoError: status.HTTP_409_CONFLICT,
    DominioError: status.HTTP_400_BAD_REQUEST,
}


def respuesta_de_error_despacho(error: DominioError) -> Response:
    return respuesta_de_error(error, ESTADOS_HTTP)
