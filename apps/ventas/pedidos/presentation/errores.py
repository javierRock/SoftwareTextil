"""Codigos HTTP de los errores del dominio de pedidos.

Punto de extension (OCP): para que un error nuevo devuelva otro codigo basta
con agregar su fila a `ESTADOS_HTTP`; las vistas no se modifican.
"""

from rest_framework import status
from rest_framework.response import Response

from apps.compartido.domain.errors import DominioError
from apps.compartido.presentation.errores import EstadosHttp, respuesta_de_error
from apps.ventas.carrito.domain.errors import CarritoError
from apps.ventas.pedidos.domain.errors import (
    CarritoNoEncontradoError,
    PedidoError,
    PedidoNoEncontradoError,
)

# Generar un pedido cierra el carrito de origen, asi que este modulo tambien
# traduce los errores del agregado carrito.
ESTADOS_HTTP: EstadosHttp = {
    PedidoNoEncontradoError: status.HTTP_404_NOT_FOUND,
    CarritoNoEncontradoError: status.HTTP_404_NOT_FOUND,
    PedidoError: status.HTTP_400_BAD_REQUEST,
    CarritoError: status.HTTP_400_BAD_REQUEST,
}


def respuesta_de_error_pedido(error: DominioError) -> Response:
    return respuesta_de_error(error, ESTADOS_HTTP)
