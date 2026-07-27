"""Adaptadores HTTP para los casos de uso de pagos."""

from collections.abc import Callable

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from apps.usuarios.presentation.permissions import EsAdministrador, EsCliente
from apps.ventas.pagos.application.services import ServicioPagos
from apps.ventas.pagos.domain.excepciones import (
    ErrorPago,
    PagoNoEncontrado,
    PagoPedidoDuplicado,
    PagoYaProcesado,
    PedidoNoAdmitePago,
    PedidoNoEncontrado,
    PedidoNoPerteneceCliente,
)
from apps.ventas.pagos.domain.pago import Pago
from apps.ventas.pagos.domain.repositorios import PaginaPagos
from apps.ventas.pagos.infrastructure.pedidos import DjangoRepositorioPedidoPago
from apps.ventas.pagos.infrastructure.repositories import DjangoRepositorioPago
from apps.ventas.pagos.presentation.serializers import (
    CrearPagoSerializer,
    FiltroPagosSerializer,
    PagoSerializer,
)

ERRORES_NO_ENCONTRADOS = (PagoNoEncontrado, PedidoNoEncontrado)
ERRORES_PROHIBIDOS = (PedidoNoPerteneceCliente,)
ERRORES_CONFLICTO = (PagoYaProcesado, PagoPedidoDuplicado, PedidoNoAdmitePago)


def _crear_servicio() -> ServicioPagos:
    return ServicioPagos(
        DjangoRepositorioPago(),
        DjangoRepositorioPedidoPago(),
        transaction.atomic,
    )


def _respuesta_entrada_invalida(errores: dict[str, object]) -> Response:
    return Response(
        {"codigo": "entrada_invalida", "detalle": errores},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _respuesta_error(error: ErrorPago) -> Response:
    estado_http = status.HTTP_400_BAD_REQUEST
    if isinstance(error, ERRORES_NO_ENCONTRADOS):
        estado_http = status.HTTP_404_NOT_FOUND
    elif isinstance(error, ERRORES_PROHIBIDOS):
        estado_http = status.HTTP_403_FORBIDDEN
    elif isinstance(error, ERRORES_CONFLICTO):
        estado_http = status.HTTP_409_CONFLICT
    return Response(
        {"codigo": error.codigo, "detalle": str(error)},
        status=estado_http,
    )


def _ejecutar_caso_uso(
    caso_uso: Callable[[], Pago],
    estado_exitoso: int = status.HTTP_200_OK,
) -> Response:
    try:
        resultado = caso_uso()
    except ErrorPago as error:
        return _respuesta_error(error)
    return Response(PagoSerializer(resultado).data, status=estado_exitoso)


class PagoViewSet(viewsets.ViewSet):
    """Expone pagos con autorizacion por rol y reglas en la aplicacion."""

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "create":
            clases = [EsCliente]
        elif self.action in {"aprobar", "rechazar"}:
            clases = [EsAdministrador]
        else:
            clases = [EsCliente | EsAdministrador]
        return [clase() for clase in clases]

    def list(self, request: Request) -> Response:
        serializer = FiltroPagosSerializer(data=request.query_params)
        if not serializer.is_valid():
            return _respuesta_entrada_invalida(serializer.errors)
        datos = serializer.validated_data
        try:
            resultado = _crear_servicio().listar(
                pagina=datos["pagina"],
                tamano_pagina=datos["tamano"],
                pedido_id=datos.get("pedido_id"),
                cliente_id=self._cliente_id(request),
            )
        except ErrorPago as error:
            return _respuesta_error(error)
        return self._respuesta_paginada(
            resultado,
            datos["pagina"],
            datos["tamano"],
        )

    def create(self, request: Request) -> Response:
        serializer = CrearPagoSerializer(data=request.data)
        if not serializer.is_valid():
            return _respuesta_entrada_invalida(serializer.errors)
        datos = serializer.validated_data
        return _ejecutar_caso_uso(
            lambda: _crear_servicio().registrar_pago(
                pedido_id=datos["pedido_id"],
                monto=datos["monto"],
                metodo=datos["metodo"],
                referencia=datos["referencia"],
                cliente_id=str(request.user.id),
            ),
            status.HTTP_201_CREATED,
        )

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        return _ejecutar_caso_uso(
            lambda: _crear_servicio().obtener(
                pk or "",
                cliente_id=self._cliente_id(request),
            )
        )

    @action(detail=True, methods=["post"], url_path="aprobar")
    def aprobar(self, request: Request, pk: str | None = None) -> Response:
        return _ejecutar_caso_uso(lambda: _crear_servicio().aprobar(pk or ""))

    @action(detail=True, methods=["post"], url_path="rechazar")
    def rechazar(self, request: Request, pk: str | None = None) -> Response:
        return _ejecutar_caso_uso(lambda: _crear_servicio().rechazar(pk or ""))

    @staticmethod
    def _cliente_id(request: Request) -> str | None:
        if request.user.rol.casefold() == "administrador":
            return None
        return str(request.user.id)

    @staticmethod
    def _respuesta_paginada(
        pagina: PaginaPagos,
        numero: int,
        tamano: int,
    ) -> Response:
        return Response(
            {
                "total": pagina.total,
                "pagina": numero,
                "tamano": tamano,
                "resultados": PagoSerializer(pagina.pagos, many=True).data,
            }
        )
