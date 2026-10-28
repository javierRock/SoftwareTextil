"""Pruebas del resolutor de errores HTTP que evidencian OCP.

Registrar un error nuevo es agregar una fila a la tabla del modulo: ni el
resolutor compartido ni las vistas se modifican.
"""

from rest_framework import status

from apps.compartido.domain.errors import DominioError
from apps.compartido.presentation.errores import ESTADO_POR_DEFECTO, estado_http_de
from apps.ventas.pedidos.domain.errors import (
    PedidoError,
    PedidoNoCancelableError,
    PedidoNoEncontradoError,
)
from apps.ventas.pedidos.presentation.errores import ESTADOS_HTTP


def test_error_registrado_usa_su_propio_codigo():
    assert (
        estado_http_de(PedidoNoEncontradoError(), ESTADOS_HTTP)
        == status.HTTP_404_NOT_FOUND
    )


def test_error_no_registrado_hereda_el_codigo_de_su_clase_base():
    """`PedidoNoCancelableError` no esta en la tabla: hereda el 400 de `PedidoError`."""
    assert (
        estado_http_de(PedidoNoCancelableError(), ESTADOS_HTTP)
        == status.HTTP_400_BAD_REQUEST
    )


def test_error_ajeno_a_la_tabla_cae_en_el_valor_por_defecto():
    assert estado_http_de(DominioError("cualquiera"), ESTADOS_HTTP) == (
        ESTADO_POR_DEFECTO
    )


def test_extender_la_tabla_no_exige_tocar_el_resolutor():
    """OCP: un error nuevo solo necesita su fila en la tabla del modulo."""

    class PedidoBloqueadoError(PedidoError):
        def __init__(self) -> None:
            super().__init__("El pedido esta bloqueado")

    estados = {**ESTADOS_HTTP, PedidoBloqueadoError: status.HTTP_409_CONFLICT}

    assert estado_http_de(PedidoBloqueadoError(), estados) == status.HTTP_409_CONFLICT
    # Sin la fila nueva, el mismo error habria respondido el 400 de su base.
    assert (
        estado_http_de(PedidoBloqueadoError(), ESTADOS_HTTP)
        == status.HTTP_400_BAD_REQUEST
    )
