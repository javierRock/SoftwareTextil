"""Views DRF para pagos."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ventas.pagos.application.services import ServicioPagos
from apps.ventas.pagos.infrastructure.models import PagoModel
from apps.ventas.pagos.infrastructure.repositories import DjangoRepositorioPago
from apps.ventas.pagos.presentation.serializers import CrearPagoSerializer, PagoSerializer


def _servicio() -> ServicioPagos:
    return ServicioPagos(DjangoRepositorioPago())


class PagoViewSet(viewsets.ViewSet):
    def list(self, request):
        pedido_id = request.query_params.get("pedido_id")
        if pedido_id:
            pagos = PagoModel.objects.filter(pedido_id=pedido_id)
        else:
            pagos = PagoModel.objects.all()
        return Response(PagoSerializer(pagos, many=True).data)

    def create(self, request):
        serializer = CrearPagoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            pago = servicio.registrar_pago(
                pedido_id=serializer.validated_data["pedido_id"],
                monto=serializer.validated_data["monto"],
                metodo=serializer.validated_data["metodo"],
                referencia=serializer.validated_data["referencia"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        model = PagoModel.objects.get(id=pago.id)
        return Response(PagoSerializer(model).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            pago = _servicio().obtener(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        model = PagoModel.objects.get(id=pago.id)
        return Response(PagoSerializer(model).data)

    @action(detail=True, methods=["post"], url_path="aprobar")
    def aprobar(self, request, pk=None):
        servicio = _servicio()
        try:
            pago = servicio.aprobar(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        model = PagoModel.objects.get(id=pago.id)
        return Response(PagoSerializer(model).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="rechazar")
    def rechazar(self, request, pk=None):
        servicio = _servicio()
        try:
            pago = servicio.rechazar(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        model = PagoModel.objects.get(id=pago.id)
        return Response(PagoSerializer(model).data, status=status.HTTP_200_OK)
