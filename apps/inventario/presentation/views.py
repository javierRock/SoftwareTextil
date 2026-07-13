"""Views DRF para inventario."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.inventario.application.services import ServicioInventario
from apps.inventario.infrastructure.models import MovimientoInventarioModel, StockPrendaModel
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioAlertaStock,
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)
from apps.inventario.presentation.serializers import (
    AjusteStockSerializer,
    CrearStockSerializer,
    MovimientoSerializer,
    MovimientoStockSerializer,
    StockSerializer,
)


def _servicio() -> ServicioInventario:
    return ServicioInventario(
        DjangoRepositorioInventario(),
        DjangoRepositorioMovimiento(),
        DjangoRepositorioAlertaStock(),
    )


class StockViewSet(viewsets.ViewSet):
    def list(self, request):
        stock_list = _servicio().listar_stock()
        return Response(StockSerializer(stock_list, many=True).data)

    def create(self, request):
        serializer = CrearStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            stock = servicio.crear_stock(
                prenda_id=serializer.validated_data["prenda_id"],
                stock_inicial=serializer.validated_data["stock_inicial"],
                stock_minimo=serializer.validated_data["stock_minimo"],
                ubicacion=serializer.validated_data["ubicacion"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(StockSerializer(stock).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        stock = _servicio().consultar_stock(pk)
        if stock is None:
            return Response({"error": "Stock no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        return Response(StockSerializer(stock).data)

    @action(detail=False, methods=["post"], url_path="ingresos")
    def registrar_ingreso(self, request):
        serializer = MovimientoStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            movimiento = servicio.registrar_ingreso(
                prenda_id=serializer.validated_data["prenda_id"],
                cantidad=serializer.validated_data["cantidad"],
                motivo=serializer.validated_data["motivo"],
                usuario_id=serializer.validated_data["usuario_id"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(MovimientoSerializer(movimiento).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="salidas")
    def registrar_salida(self, request):
        serializer = MovimientoStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            movimiento = servicio.registrar_salida(
                prenda_id=serializer.validated_data["prenda_id"],
                cantidad=serializer.validated_data["cantidad"],
                motivo=serializer.validated_data["motivo"],
                usuario_id=serializer.validated_data["usuario_id"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(MovimientoSerializer(movimiento).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="ajustes")
    def ajustar(self, request):
        serializer = AjusteStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            movimiento = servicio.ajustar_stock(
                prenda_id=serializer.validated_data["prenda_id"],
                nueva_cantidad=serializer.validated_data["nueva_cantidad"],
                motivo=serializer.validated_data["motivo"],
                usuario_id=serializer.validated_data["usuario_id"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(MovimientoSerializer(movimiento).data, status=status.HTTP_201_CREATED)


class MovimientoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoInventarioModel.objects.all()
    serializer_class = MovimientoSerializer
