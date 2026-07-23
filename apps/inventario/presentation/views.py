"""Views DRF para inventario."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.catalogo.infrastructure.repositories import DjangoRepositorioPrenda
from apps.inventario.domain.excepciones import (
    CantidadInvalida,
    PrendaNoEncontrada,
    StockInsuficiente,
    StockNoEncontrado,
    UsuarioResponsableRequerido,
)
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
        DjangoRepositorioPrenda(),
    )


def _usuario_responsable_desde_solicitud(request, usuario_id: str | None) -> str:
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        return str(request.user.id)
    if usuario_id:
        return usuario_id
    raise UsuarioResponsableRequerido("Usuario responsable requerido")


def _manejar_error(exc: Exception) -> tuple[dict[str, str], int]:
    if isinstance(exc, (CantidadInvalida, StockInsuficiente, UsuarioResponsableRequerido)):
        return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST
    if isinstance(exc, (PrendaNoEncontrada, StockNoEncontrado)):
        return {"error": str(exc)}, status.HTTP_404_NOT_FOUND
    return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST


class StockViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

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
        except CantidadInvalida as exc:
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
                usuario_id=_usuario_responsable_desde_solicitud(request, serializer.validated_data.get("usuario_id")),
            )
        except (CantidadInvalida, PrendaNoEncontrada, StockInsuficiente, StockNoEncontrado, UsuarioResponsableRequerido) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
        model = MovimientoInventarioModel.objects.get(id=movimiento.id)
        return Response(MovimientoSerializer(model).data, status=status.HTTP_201_CREATED)

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
                usuario_id=_usuario_responsable_desde_solicitud(request, serializer.validated_data.get("usuario_id")),
            )
        except (CantidadInvalida, PrendaNoEncontrada, StockInsuficiente, StockNoEncontrado, UsuarioResponsableRequerido) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
        model = MovimientoInventarioModel.objects.get(id=movimiento.id)
        return Response(MovimientoSerializer(model).data, status=status.HTTP_201_CREATED)

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
                usuario_id=_usuario_responsable_desde_solicitud(request, serializer.validated_data.get("usuario_id")),
            )
        except (CantidadInvalida, PrendaNoEncontrada, StockInsuficiente, StockNoEncontrado, UsuarioResponsableRequerido) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
        model = MovimientoInventarioModel.objects.get(id=movimiento.id)
        return Response(MovimientoSerializer(model).data, status=status.HTTP_201_CREATED)


class MovimientoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = MovimientoInventarioModel.objects.all()
    serializer_class = MovimientoSerializer
