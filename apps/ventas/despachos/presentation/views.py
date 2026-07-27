"""Views DRF para despachos."""

from typing import ClassVar

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.compartido.domain.errors import DominioError
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)
from apps.usuarios.presentation.permissions import EsAdministrador
from apps.ventas.despachos.application.services import ServicioDespachos
from apps.ventas.despachos.infrastructure.repositories import (
    DjangoRepositorioDespacho,
)
from apps.ventas.despachos.presentation.errores import respuesta_de_error_despacho
from apps.ventas.despachos.presentation.serializers import (
    ConfirmarDespachoSerializer,
    DespachoSerializer,
    PrepararDespachoSerializer,
    ProgramarDespachoSerializer,
)
from apps.ventas.pedidos.infrastructure.repositories import DjangoRepositorioPedido
from apps.ventas.permissions import EsEncargadoInventario
from apps.ventas.presentation.errores import respuesta_entrada_invalida


def _servicio() -> ServicioDespachos:
    return ServicioDespachos(
        DjangoRepositorioDespacho(),
        DjangoRepositorioPedido(),
        transaction.atomic,
        DjangoRepositorioInventario(),
        DjangoRepositorioMovimiento(),
    )


class DespachoViewSet(viewsets.ViewSet):
    permission_classes: ClassVar[list[object]] = [
        EsAdministrador | EsEncargadoInventario
    ]

    def list(self, request):
        despachos = _servicio().listar()
        return Response(DespachoSerializer(despachos, many=True).data)

    def create(self, request):
        serializer = ProgramarDespachoSerializer(data=request.data)
        if not serializer.is_valid():
            return respuesta_entrada_invalida(serializer.errors)
        datos = serializer.validated_data
        try:
            despacho = _servicio().programar(
                pedido_id=str(datos["pedido_id"]),
                direccion_entrega=datos["direccion_entrega"],
            )
        except DominioError as error:
            return respuesta_de_error_despacho(error)
        return Response(
            DespachoSerializer(despacho).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None):
        try:
            despacho = _servicio().consultar(pk)
        except DominioError as error:
            return respuesta_de_error_despacho(error)
        return Response(DespachoSerializer(despacho).data)

    @action(detail=True, methods=["post"], url_path="preparar")
    def preparar(self, request, pk=None):
        serializer = PrepararDespachoSerializer(data=request.data)
        if not serializer.is_valid():
            return respuesta_entrada_invalida(serializer.errors)
        try:
            despacho = _servicio().preparar(
                despacho_id=pk,
                responsable_id=str(request.user.id),
            )
        except DominioError as error:
            return respuesta_de_error_despacho(error)
        return Response(DespachoSerializer(despacho).data)

    @action(detail=True, methods=["post"], url_path="confirmar")
    def confirmar(self, request, pk=None):
        serializer = ConfirmarDespachoSerializer(data=request.data)
        if not serializer.is_valid():
            return respuesta_entrada_invalida(serializer.errors)
        datos = serializer.validated_data
        try:
            despacho = _servicio().confirmar(
                despacho_id=pk,
                serie=datos["serie"],
                numero=datos["numero"],
                transportista=datos["transportista"],
            )
        except DominioError as error:
            return respuesta_de_error_despacho(error)
        return Response(DespachoSerializer(despacho).data)

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        try:
            despacho = _servicio().cancelar(pk)
        except DominioError as error:
            return respuesta_de_error_despacho(error)
        return Response(DespachoSerializer(despacho).data)
