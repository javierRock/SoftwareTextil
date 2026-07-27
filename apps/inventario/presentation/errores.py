"""Codigos HTTP de los errores del dominio de inventario.

Punto de extension (OCP): para que un error nuevo devuelva otro codigo basta
con agregar su fila a `ESTADOS_HTTP`; las vistas no se modifican.
"""

from rest_framework import status
from rest_framework.response import Response

from apps.compartido.presentation.errores import EstadosHttp, respuesta_de_error
from apps.inventario.domain.excepciones import (
    CantidadInvalidaError,
    CategoriaNoEncontradaError,
    InventarioError,
    ReservaInvalidaError,
    StockInsuficienteError,
    StockNoEncontradoError,
    StockYaExisteError,
    UsuarioResponsableRequeridoError,
    VarianteNoEncontradaError,
)

ESTADOS_HTTP: EstadosHttp = {
    VarianteNoEncontradaError: status.HTTP_404_NOT_FOUND,
    StockNoEncontradoError: status.HTTP_404_NOT_FOUND,
    CategoriaNoEncontradaError: status.HTTP_404_NOT_FOUND,
    StockYaExisteError: status.HTTP_409_CONFLICT,
    UsuarioResponsableRequeridoError: status.HTTP_401_UNAUTHORIZED,
    CantidadInvalidaError: status.HTTP_400_BAD_REQUEST,
    StockInsuficienteError: status.HTTP_400_BAD_REQUEST,
    ReservaInvalidaError: status.HTTP_400_BAD_REQUEST,
    InventarioError: status.HTTP_400_BAD_REQUEST,
}


def respuesta_de_error_inventario(error: InventarioError) -> Response:
    return respuesta_de_error(error, ESTADOS_HTTP)
