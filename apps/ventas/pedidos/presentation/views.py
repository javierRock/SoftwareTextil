"""Views DRF para pedidos."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ventas.carrito.infrastructure.repositories import DjangoRepositorioCarrito
from apps.ventas.pedidos.application.services import ServicioPedidos
from apps.ventas.pedidos.infrastructure.models import PedidoModel
from apps.ventas.pedidos.infrastructure.repositories import DjangoRepositorioPedido
from apps.ventas.pedidos.presentation.serializers import CrearPedidoSerializer, PedidoSerializer


def _servicio() -> ServicioPedidos:
    return ServicioPedidos(DjangoRepositorioPedido(), DjangoRepositorioCarrito())


class PedidoViewSet(viewsets.ViewSet):
    def list(self, request):
        cliente_id = request.query_params.get("cliente_id")
        if cliente_id:
            pedidos = _servicio().listar_por_cliente(cliente_id)
            return Response(PedidoSerializer(pedidos, many=True).data)
        return Response(PedidoSerializer(PedidoModel.objects.all(), many=True).data)

    def create(self, request):
        serializer = CrearPedidoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            pedido = servicio.generar_desde_carrito(
                carrito_id=serializer.validated_data["carrito_id"],
                cliente_id=serializer.validated_data["cliente_id"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            pedido = _servicio().obtener_pedido(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(PedidoSerializer(pedido).data)

    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        servicio = _servicio()
        try:
            pedido = servicio.cancelar(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_200_OK)
