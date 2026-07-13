"""Views DRF para catalogo."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalogo.application.services import ServicioCatalogo
from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel, TipoProductoModel
from apps.catalogo.infrastructure.repositories import DjangoRepositorioCatalogo, DjangoRepositorioPrenda
from apps.catalogo.presentation.serializers import (
    CategoriaSerializer,
    CrearPrendaSerializer,
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
        return Response({"id": prenda.id, "nombre": prenda.nombre}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        servicio = _servicio()
        try:
            servicio.desactivar_prenda(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"mensaje": "Prenda desactivada"}, status=status.HTTP_200_OK)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = CategoriaModel.objects.all()
    serializer_class = CategoriaSerializer

    def create(self, request, *args, **kwargs):
        servicio = _servicio()
        categoria = servicio.crear_categoria(
            nombre=request.data.get("nombre", ""),
            descripcion=request.data.get("descripcion", ""),
        )
        return Response(CategoriaSerializer(categoria).data, status=status.HTTP_201_CREATED)


class TipoProductoViewSet(viewsets.ModelViewSet):
    queryset = TipoProductoModel.objects.all()
    serializer_class = TipoProductoSerializer

    def create(self, request, *args, **kwargs):
        servicio = _servicio()
        tipo = servicio.crear_tipo_producto(
            nombre=request.data.get("nombre", ""),
            atributos_base=request.data.get("atributos_base"),
        )
        return Response(TipoProductoSerializer(tipo).data, status=status.HTTP_201_CREATED)
