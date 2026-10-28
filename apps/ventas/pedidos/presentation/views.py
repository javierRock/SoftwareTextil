"""Views DRF para pedidos.

La vista tiene una sola responsabilidad (SRP): traducir HTTP a casos de uso y
el resultado a una respuesta. No consulta el ORM ni instancia repositorios
concretos; los recibe de las fabricas del modulo a traves de atributos de
clase, que las pruebas pueden reemplazar por dobles en memoria (DIP).
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from apps.compartido.domain.errors import DominioError
from apps.usuarios.presentation.permissions import (
    EsAdministrador,
    EsCliente,
    EsPersonalInventario,
)
from apps.ventas.pedidos.domain.errors import PedidoNoPerteneceAClienteError
from apps.ventas.pedidos.infrastructure.factories import (
    construir_consulta_pedidos,
    construir_servicio_pedidos,
)
from apps.ventas.pedidos.presentation.errores import respuesta_de_error_pedido
from apps.ventas.pedidos.presentation.serializers import (
    CrearPedidoSerializer,
    PedidoSerializer,
)
from apps.ventas.presentation.errores import respuesta_entrada_invalida


class PedidoViewSet(viewsets.ViewSet):
    construir_servicio = staticmethod(construir_servicio_pedidos)
    construir_consulta = staticmethod(construir_consulta_pedidos)

    def get_permissions(self) -> list[BasePermission]:
        clases = [EsCliente | EsAdministrador | EsPersonalInventario]
        if self.action in {"create", "cancelar"}:
            clases = [EsCliente]
        return [clase() for clase in clases]

    def list(self, request):
        cliente_id = str(request.user.id)
        if request.user.rol.casefold() in {
            "administrador",
            "encargado de inventario",
        }:
            cliente_id = request.query_params.get("cliente_id")
        pedidos = self.construir_consulta().listar(cliente_id)
        return Response(PedidoSerializer(pedidos, many=True).data)

    def create(self, request):
        serializer = CrearPedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return respuesta_entrada_invalida(serializer.errors)
        try:
            pedido = self.construir_servicio().generar_desde_carrito(
                carrito_id=serializer.validated_data["carrito_id"],
                cliente_id=str(request.user.id),
            )
        except DominioError as exc:
            return respuesta_de_error_pedido(exc)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            pedido = self.construir_consulta().obtener(pk)
            if (
                request.user.rol.casefold()
                not in {"administrador", "encargado de inventario"}
                and pedido.cliente_id != str(request.user.id)
            ):
                raise PedidoNoPerteneceAClienteError
        except DominioError as exc:
            return respuesta_de_error_pedido(exc)
        return Response(PedidoSerializer(pedido).data)

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        try:
            pedido = self.construir_servicio().cancelar(
                pk, cliente_id=str(request.user.id)
            )
        except DominioError as exc:
            return respuesta_de_error_pedido(exc)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_200_OK)
