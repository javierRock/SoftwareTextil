"""Views DRF para inventario."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.inventario.application.services import ServicioInventario
from apps.inventario.infrastructure.models import MovimientoInventarioModel
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
        datos = serializer.validated_data
        try:
            stock = _servicio().crear_stock(
                variante_id=str(datos["variante_id"]),
                stock_inicial=datos["stock_inicial"],
                stock_minimo=datos["stock_minimo"],
                ubicacion=datos["ubicacion"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(StockSerializer(stock).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        stock = _servicio().consultar_stock(pk)
        if stock is None:
            return Response(
                {"error": "Stock no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(StockSerializer(stock).data)

    @action(detail=False, methods=["post"], url_path="ingresos")
    def registrar_ingreso(self, request):
        return self._registrar_movimiento(
            request,
            MovimientoStockSerializer,
            self._aplicar_ingreso,
        )

    @action(detail=False, methods=["post"], url_path="salidas")
    def registrar_salida(self, request):
        return self._registrar_movimiento(
            request,
            MovimientoStockSerializer,
            self._aplicar_salida,
        )

    @action(detail=False, methods=["post"], url_path="ajustes")
    def ajustar(self, request):
        return self._registrar_movimiento(
            request,
            AjusteStockSerializer,
            self._aplicar_ajuste,
        )

    @staticmethod
    def _aplicar_ingreso(servicio: ServicioInventario, datos: dict):
        return servicio.registrar_ingreso(
            variante_id=str(datos["variante_id"]),
            cantidad=datos["cantidad"],
            motivo=datos["motivo"],
            usuario_id=str(datos["usuario_id"]),
        )

    @staticmethod
    def _aplicar_salida(servicio: ServicioInventario, datos: dict):
        return servicio.registrar_salida(
            variante_id=str(datos["variante_id"]),
            cantidad=datos["cantidad"],
            motivo=datos["motivo"],
            usuario_id=str(datos["usuario_id"]),
        )

    @staticmethod
    def _aplicar_ajuste(servicio: ServicioInventario, datos: dict):
        return servicio.ajustar_stock(
            variante_id=str(datos["variante_id"]),
            nueva_cantidad=datos["nueva_cantidad"],
            motivo=datos["motivo"],
            usuario_id=str(datos["usuario_id"]),
        )

    @staticmethod
    def _registrar_movimiento(request, clase_serializer, aplicar):
        """Las tres acciones comparten validar, aplicar y devolver 201."""
        serializer = clase_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            movimiento = aplicar(_servicio(), serializer.validated_data)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        model = MovimientoInventarioModel.objects.get(id=movimiento.id)
        return Response(
            MovimientoSerializer(model).data,
            status=status.HTTP_201_CREATED,
        )


class MovimientoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoInventarioModel.objects.all()
    serializer_class = MovimientoSerializer
