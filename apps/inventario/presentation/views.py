"""Views DRF para inventario."""

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.catalogo.infrastructure.repositories import DjangoRepositorioPrenda
from apps.catalogo.infrastructure.repositories import DjangoRepositorioCatalogo
from apps.inventario.domain.excepciones import (
    CantidadInvalida,
    CategoriaNoEncontrada,
    PrendaNoEncontrada,
    StockInsuficiente,
    StockNoEncontrado,
    StockYaExiste,
    UsuarioResponsableRequerido,
)
from apps.inventario.application.services import ServicioInventario
from apps.inventario.application.reportes import ServicioReporteInventario
from apps.inventario.infrastructure.models import MovimientoInventarioModel
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioAlertaStock,
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)
from apps.inventario.presentation.serializers import (
    AjusteStockSerializer,
    CategoriaStockAgrupadaSerializer,
    CrearStockSerializer,
    MovimientoSerializer,
    MovimientoStockSerializer,
    PrendaStockBajoMinimoSerializer,
    ReporteInventarioQuerySerializer,
    StockSerializer,
)


def _servicio() -> ServicioInventario:
    return ServicioInventario(
        DjangoRepositorioInventario(),
        DjangoRepositorioMovimiento(),
        DjangoRepositorioAlertaStock(),
        DjangoRepositorioPrenda(),
        DjangoRepositorioCatalogo(),
    )


def _servicio_reporte() -> ServicioReporteInventario:
    return ServicioReporteInventario(_servicio(), DjangoRepositorioPrenda())


def _usuario_responsable_desde_solicitud(request) -> str:
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        return str(request.user.id)
    raise UsuarioResponsableRequerido("Usuario responsable requerido")


def _manejar_error(exc: Exception) -> tuple[dict[str, str], int]:
    if isinstance(exc, (CantidadInvalida, StockInsuficiente, UsuarioResponsableRequerido)):
        return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST
    if isinstance(exc, (PrendaNoEncontrada, StockNoEncontrado, CategoriaNoEncontrada)):
        return {"error": str(exc)}, status.HTTP_404_NOT_FOUND
    if isinstance(exc, StockYaExiste):
        return {"error": str(exc)}, status.HTTP_409_CONFLICT
    return {"error": str(exc)}, status.HTTP_400_BAD_REQUEST


class StockViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        stock_list = _servicio().listar_stock()
        return Response(StockSerializer(stock_list, many=True).data)

    @action(detail=False, methods=["get"], url_path="por-categoria")
    def por_categoria(self, request):
        categoria_id = request.query_params.get("categoria_id") or None
        servicio = _servicio()
        try:
            resumen = servicio.listar_stock_por_categoria(categoria_id)
        except CategoriaNoEncontrada as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
        return Response(CategoriaStockAgrupadaSerializer(resumen, many=True).data)

    @action(detail=False, methods=["get"], url_path="bajo-minimo")
    def bajo_minimo(self, request):
        alertas = _servicio().listar_stock_bajo_minimo()
        return Response(PrendaStockBajoMinimoSerializer(alertas, many=True).data)

    @action(detail=False, methods=["get"], url_path="reporte")
    def reporte(self, request):
        serializer = ReporteInventarioQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        servicio = _servicio_reporte()
        try:
            archivo = servicio.generar_archivo(
                formato=serializer.validated_data["formato"],
                categoria_id=serializer.validated_data.get("categoria_id") or None,
            )
        except (CategoriaNoEncontrada, ValueError) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)

        respuesta = HttpResponse(archivo.contenido, content_type=archivo.content_type)
        respuesta["Content-Disposition"] = f'attachment; filename="{archivo.nombre_archivo}"'
        return respuesta

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
        except (CantidadInvalida, PrendaNoEncontrada, StockYaExiste) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
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
                usuario_id=_usuario_responsable_desde_solicitud(request),
            )
        except (CantidadInvalida, PrendaNoEncontrada, StockInsuficiente, StockNoEncontrado, UsuarioResponsableRequerido) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
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
                usuario_id=_usuario_responsable_desde_solicitud(request),
            )
        except (CantidadInvalida, PrendaNoEncontrada, StockInsuficiente, StockNoEncontrado, UsuarioResponsableRequerido) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
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
                usuario_id=_usuario_responsable_desde_solicitud(request),
            )
        except (CantidadInvalida, PrendaNoEncontrada, StockInsuficiente, StockNoEncontrado, UsuarioResponsableRequerido) as exc:
            body, code = _manejar_error(exc)
            return Response(body, status=code)
        return Response(MovimientoSerializer(movimiento).data, status=status.HTTP_201_CREATED)


class MovimientoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    queryset = MovimientoInventarioModel.objects.select_related("stock").all()
    serializer_class = MovimientoSerializer
