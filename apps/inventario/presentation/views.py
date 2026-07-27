"""Views DRF para inventario."""

from typing import ClassVar

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.catalogo.infrastructure.repositories import (
    DjangoRepositorioCatalogo,
    DjangoRepositorioVariante,
)
from apps.inventario.application.services import ServicioInventario
from apps.inventario.domain.excepciones import (
    InventarioError,
    UsuarioResponsableRequeridoError,
)
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioAlertaStock,
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)
from apps.inventario.presentation.errores import respuesta_de_error_inventario
from apps.inventario.presentation.serializers import (
    AjusteStockSerializer,
    CategoriaStockAgrupadaSerializer,
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
        DjangoRepositorioVariante(),
        DjangoRepositorioCatalogo(),
    )


def _responsable(request) -> str:
    """El responsable del movimiento sale de la sesion autenticada.

    Tomarlo del cuerpo de la peticion permitiria que cualquiera registrara
    movimientos a nombre de otro usuario.
    """
    usuario = getattr(request, "user", None)
    if usuario is None or not usuario.is_authenticated:
        raise UsuarioResponsableRequeridoError("Usuario responsable requerido")
    return str(usuario.id)


class StockViewSet(viewsets.ViewSet):
    permission_classes: ClassVar[list] = [IsAuthenticated]

    def list(self, request):
        return Response(StockSerializer(_servicio().listar_stock(), many=True).data)

    @action(detail=False, methods=["get"], url_path="por-categoria")
    def por_categoria(self, request):
        categoria_id = request.query_params.get("categoria_id") or None
        try:
            resumen = _servicio().listar_stock_por_categoria(categoria_id)
        except InventarioError as error:
            return respuesta_de_error_inventario(error)
        return Response(CategoriaStockAgrupadaSerializer(resumen, many=True).data)

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
        except InventarioError as error:
            return respuesta_de_error_inventario(error)
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
    def _aplicar_ingreso(servicio: ServicioInventario, datos: dict, responsable: str):
        return servicio.registrar_ingreso(
            variante_id=str(datos["variante_id"]),
            cantidad=datos["cantidad"],
            motivo=datos["motivo"],
            usuario_id=responsable,
        )

    @staticmethod
    def _aplicar_salida(servicio: ServicioInventario, datos: dict, responsable: str):
        return servicio.registrar_salida(
            variante_id=str(datos["variante_id"]),
            cantidad=datos["cantidad"],
            motivo=datos["motivo"],
            usuario_id=responsable,
        )

    @staticmethod
    def _aplicar_ajuste(servicio: ServicioInventario, datos: dict, responsable: str):
        return servicio.ajustar_stock(
            variante_id=str(datos["variante_id"]),
            nueva_cantidad=datos["nueva_cantidad"],
            motivo=datos["motivo"],
            usuario_id=responsable,
        )

    @staticmethod
    def _registrar_movimiento(request, clase_serializer, aplicar):
        """Las tres acciones comparten validar, aplicar y devolver 201."""
        serializer = clase_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            responsable = _responsable(request)
            movimiento = aplicar(_servicio(), serializer.validated_data, responsable)
        except InventarioError as error:
            return respuesta_de_error_inventario(error)
        return Response(
            MovimientoSerializer(movimiento).data,
            status=status.HTTP_201_CREATED,
        )


class MovimientoViewSet(viewsets.ViewSet):
    permission_classes: ClassVar[list] = [IsAuthenticated]

    def list(self, request):
        stock_id = request.query_params.get("stock_id")
        if not stock_id:
            return Response(
                {"error": "Indica el stock cuyos movimientos quieres consultar"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        movimientos = _servicio().listar_movimientos(stock_id)
        return Response(MovimientoSerializer(movimientos, many=True).data)
