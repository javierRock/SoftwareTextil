"""Views DRF para catalogo."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalogo.application.services import ServicioCatalogo
from apps.catalogo.infrastructure.models import PrendaModel
from apps.catalogo.infrastructure.repositories import DjangoRepositorioCatalogo, DjangoRepositorioPrenda
from apps.catalogo.presentation.serializers import (
    ActualizarCategoriaSerializer,
    ActualizarTipoProductoSerializer,
    CategoriaSerializer,
    CrearCategoriaSerializer,
    CrearPrendaSerializer,
    CrearTipoProductoSerializer,
    PrendaCreadaSerializer,
    PrendaSerializer,
    TipoProductoSerializer,
)


def _servicio() -> ServicioCatalogo:
    return ServicioCatalogo(DjangoRepositorioPrenda(), DjangoRepositorioCatalogo())


class PrendaViewSet(viewsets.ModelViewSet):
    queryset = PrendaModel.objects.all()
    serializer_class = PrendaSerializer

    def create(self, request, *args, **kwargs):
        serializer = CrearPrendaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            prenda = servicio.crear_prenda(
                nombre=serializer.validated_data["nombre"],
                descripcion=serializer.validated_data["descripcion"],
                precio_monto=serializer.validated_data["precio_monto"],
                precio_moneda=serializer.validated_data["precio_moneda"],
                categoria_id=serializer.validated_data["categoria_id"],
                registrado_por=serializer.validated_data.get("registrado_por"),
                tipo_producto_id=serializer.validated_data.get("tipo_producto_id"),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PrendaCreadaSerializer(prenda).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        servicio = _servicio()
        try:
            servicio.desactivar_prenda(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"mensaje": "Prenda desactivada"}, status=status.HTTP_200_OK)


class CategoriaViewSet(viewsets.ViewSet):
    def list(self, request):
        categorias = _servicio().listar_categorias()
        return Response(CategoriaSerializer(categorias, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            categoria = _servicio().buscar_categoria(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(CategoriaSerializer(categoria).data)

    def create(self, request, *args, **kwargs):
        serializer = CrearCategoriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            categoria = _servicio().crear_categoria(**serializer.validated_data)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CategoriaSerializer(categoria).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=False)

    def partial_update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=True)

    def _actualizar(self, request, pk, parcial):
        servicio = _servicio()
        try:
            actual = servicio.buscar_categoria(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = ActualizarCategoriaSerializer(data=request.data, partial=parcial)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        try:
            categoria = servicio.actualizar_categoria(
                pk,
                nombre=datos.get("nombre", actual.nombre),
                descripcion=datos.get("descripcion", actual.descripcion),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(CategoriaSerializer(categoria).data)


class TipoProductoViewSet(viewsets.ViewSet):
    def list(self, request):
        tipos = _servicio().listar_tipos()
        return Response(TipoProductoSerializer(tipos, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            tipo = _servicio().buscar_tipo(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(TipoProductoSerializer(tipo).data)

    def create(self, request, *args, **kwargs):
        serializer = CrearTipoProductoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tipo = _servicio().crear_tipo_producto(**serializer.validated_data)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TipoProductoSerializer(tipo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=False)

    def partial_update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=True)

    def _actualizar(self, request, pk, parcial):
        servicio = _servicio()
        try:
            actual = servicio.buscar_tipo(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        serializer = ActualizarTipoProductoSerializer(data=request.data, partial=parcial)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        try:
            tipo = servicio.actualizar_tipo_producto(
                pk,
                nombre=datos.get("nombre", actual.nombre),
                atributos_base=datos.get("atributos_base", actual.atributos_base),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TipoProductoSerializer(tipo).data)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        return self._cambiar_estado(pk, activar=True)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        return self._cambiar_estado(pk, activar=False)

    def _cambiar_estado(self, pk, activar):
        servicio = _servicio()
        try:
            if activar:
                tipo = servicio.activar_tipo_producto(pk)
            else:
                tipo = servicio.desactivar_tipo_producto(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(TipoProductoSerializer(tipo).data)
