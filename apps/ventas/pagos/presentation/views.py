"""Adaptadores HTTP para los casos de uso de pagos."""

from collections.abc import Callable

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.ventas.pagos.application.services import ServicioPagos
from apps.ventas.pagos.domain.excepciones import (
    ErrorPago,
    PagoNoEncontrado,
    PagoYaProcesado,
)
from apps.ventas.pagos.domain.pago import Pago
from apps.ventas.pagos.infrastructure.repositories import DjangoRepositorioPago
from apps.ventas.pagos.presentation.serializers import (
    CrearPagoSerializer,
    FiltroPagosSerializer,
    PagoSerializer,
)

ESTADOS_HTTP_ERROR: dict[type[ErrorPago], int] = {
    PagoNoEncontrado: status.HTTP_404_NOT_FOUND,
    PagoYaProcesado: status.HTTP_409_CONFLICT,
}


def _crear_servicio() -> ServicioPagos:
    return ServicioPagos(DjangoRepositorioPago())


def _respuesta_entrada_invalida(errores: dict[str, object]) -> Response:
    return Response(
        {"codigo": "entrada_invalida", "detalle": errores},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _respuesta_error(error: ErrorPago) -> Response:
    estado_http = ESTADOS_HTTP_ERROR.get(type(error), status.HTTP_400_BAD_REQUEST)
    return Response(
        {"codigo": error.codigo, "detalle": str(error)},
        status=estado_http,
    )


def _ejecutar_caso_uso(
    caso_uso: Callable[[], Pago | list[Pago]],
    estado_exitoso: int = status.HTTP_200_OK,
) -> Response:
    try:
        resultado = caso_uso()
    except ErrorPago as error:
        return _respuesta_error(error)
    serializer = PagoSerializer(resultado, many=isinstance(resultado, list))
    return Response(serializer.data, status=estado_exitoso)


class PagoViewSet(viewsets.ViewSet):
    """Expone pagos como recursos REST y delega las reglas al servicio."""

    def list(self, request: Request) -> Response:
        serializer = FiltroPagosSerializer(data=request.query_params)
        if not serializer.is_valid():
            return _respuesta_entrada_invalida(serializer.errors)
        pedido_id = serializer.validated_data.get("pedido_id")
        servicio = _crear_servicio()
        if pedido_id is not None:
            return _ejecutar_caso_uso(lambda: servicio.listar_por_pedido(pedido_id))
        return _ejecutar_caso_uso(servicio.listar)

    def create(self, request: Request) -> Response:
        serializer = CrearPagoSerializer(data=request.data)
        if not serializer.is_valid():
            return _respuesta_entrada_invalida(serializer.errors)
        datos = serializer.validated_data
        servicio = _crear_servicio()
        return _ejecutar_caso_uso(
            lambda: servicio.registrar_pago(
                pedido_id=datos["pedido_id"],
                monto=datos["monto"],
                metodo=datos["metodo"],
                referencia=datos["referencia"],
            ),
            status.HTTP_201_CREATED,
        )

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        return _ejecutar_caso_uso(lambda: _crear_servicio().obtener(pk or ""))

    @action(detail=True, methods=["post"], url_path="aprobar")
    def aprobar(self, request: Request, pk: str | None = None) -> Response:
        return _ejecutar_caso_uso(lambda: _crear_servicio().aprobar(pk or ""))

    @action(detail=True, methods=["post"], url_path="rechazar")
    def rechazar(self, request: Request, pk: str | None = None) -> Response:
        return _ejecutar_caso_uso(lambda: _crear_servicio().rechazar(pk or ""))
