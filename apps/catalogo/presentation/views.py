"""Views DRF para catalogo."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.catalogo.application.services import ServicioCatalogo
from apps.catalogo.infrastructure.models import PrendaModel
from apps.catalogo.infrastructure.repositories import (
    DjangoRepositorioCatalogo,
    DjangoRepositorioPrenda,
)
from apps.catalogo.presentation.errors import ManejoErroresCatalogoMixin
from apps.catalogo.presentation.serializers import (
    ActualizarCategoriaSerializer,
    ActualizarPrendaSerializer,
    ActualizarTipoProductoSerializer,
    BuscarPrendasSerializer,
    CategoriaSerializer,
    CrearCategoriaSerializer,
    CrearPrendaSerializer,
    CrearTipoProductoSerializer,
    PrendaCatalogoSerializer,
    PrendaCreadaSerializer,
    PrendaSerializer,
    TipoProductoSerializer,
)


def _servicio() -> ServicioCatalogo:
    return ServicioCatalogo(DjangoRepositorioPrenda(), DjangoRepositorioCatalogo())


class PrendaViewSet(ManejoErroresCatalogoMixin, viewsets.ModelViewSet):
    queryset = PrendaModel.objects.all()
    serializer_class = PrendaSerializer
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def list(self, request, *args, **kwargs):
        parametros = BuscarPrendasSerializer(data=request.query_params)
        parametros.is_valid(raise_exception=True)
        prendas = _servicio().buscar_prendas(**parametros.validated_data)
        return Response(PrendaCatalogoSerializer(prendas, many=True).data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        prenda = _servicio().buscar_prenda(pk)
        return Response(PrendaCatalogoSerializer(prenda).data)

    def create(self, request, *args, **kwargs):
        serializer = CrearPrendaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        prenda = servicio.crear_prenda(
            nombre=serializer.validated_data["nombre"],
            descripcion=serializer.validated_data["descripcion"],
            precio_monto=serializer.validated_data["precio_monto"],
            precio_moneda=serializer.validated_data["precio_moneda"],
            categoria_id=serializer.validated_data["categoria_id"],
            registrado_por=serializer.validated_data.get("registrado_por"),
            tipo_producto_id=serializer.validated_data.get("tipo_producto_id"),
            tallas=serializer.validated_data["tallas"],
        )
        return Response(PrendaCreadaSerializer(prenda).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None, *args, **kwargs):
        return self._actualizar(request, pk, parcial=False)

    def partial_update(self, request, pk=None, *args, **kwargs):
        return self._actualizar(request, pk, parcial=True)

    def _actualizar(self, request, pk, parcial):
        servicio = _servicio()
        actual = servicio.buscar_prenda(pk)
        serializer = ActualizarPrendaSerializer(data=request.data, partial=parcial)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        prenda = servicio.actualizar_prenda(
            prenda_id=pk,
            nombre=datos.get("nombre", actual.nombre),
            descripcion=datos.get("descripcion", actual.descripcion),
            precio_monto=datos.get("precio_monto", actual.precio.monto),
            precio_moneda=datos.get("precio_moneda", actual.precio.moneda),
            categoria_id=datos.get("categoria_id", actual.categoria_id),
            tipo_producto_id=datos.get(
                "tipo_producto_id",
                actual.tipo_producto_id,
            ),
        )
        return Response(PrendaCatalogoSerializer(prenda).data)

    @action(detail=True, methods=["post"], url_path="activar")
    def activar(self, request, pk=None):
        prenda = _servicio().activar_prenda(pk)
        return Response(PrendaCatalogoSerializer(prenda).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        prenda = _servicio().desactivar_prenda(pk)
        return Response(PrendaCatalogoSerializer(prenda).data, status=status.HTTP_200_OK)


class CategoriaViewSet(ManejoErroresCatalogoMixin, viewsets.ViewSet):
    def list(self, request):
        categorias = _servicio().listar_categorias()
        return Response(CategoriaSerializer(categorias, many=True).data)

    def retrieve(self, request, pk=None):
        categoria = _servicio().buscar_categoria(pk)
        return Response(CategoriaSerializer(categoria).data)

    def create(self, request, *args, **kwargs):
        serializer = CrearCategoriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categoria = _servicio().crear_categoria(**serializer.validated_data)
        return Response(CategoriaSerializer(categoria).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=False)

    def partial_update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=True)

    def _actualizar(self, request, pk, parcial):
        servicio = _servicio()
        actual = servicio.buscar_categoria(pk)

        serializer = ActualizarCategoriaSerializer(data=request.data, partial=parcial)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        categoria = servicio.actualizar_categoria(
            pk,
            nombre=datos.get("nombre", actual.nombre),
            descripcion=datos.get("descripcion", actual.descripcion),
        )
        return Response(CategoriaSerializer(categoria).data)


class TipoProductoViewSet(ManejoErroresCatalogoMixin, viewsets.ViewSet):
    def list(self, request):
        tipos = _servicio().listar_tipos()
        return Response(TipoProductoSerializer(tipos, many=True).data)

    def retrieve(self, request, pk=None):
        tipo = _servicio().buscar_tipo(pk)
        return Response(TipoProductoSerializer(tipo).data)

    def create(self, request, *args, **kwargs):
        serializer = CrearTipoProductoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tipo = _servicio().crear_tipo_producto(**serializer.validated_data)
        return Response(TipoProductoSerializer(tipo).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=False)

    def partial_update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=True)

    def _actualizar(self, request, pk, parcial):
        servicio = _servicio()
        actual = servicio.buscar_tipo(pk)

        serializer = ActualizarTipoProductoSerializer(data=request.data, partial=parcial)
        serializer.is_valid(raise_exception=True)
        datos = serializer.validated_data
        tipo = servicio.actualizar_tipo_producto(
            pk,
            nombre=datos.get("nombre", actual.nombre),
            atributos_base=datos.get("atributos_base", actual.atributos_base),
        )
        return Response(TipoProductoSerializer(tipo).data)

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        return self._cambiar_estado(pk, activar=True)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        return self._cambiar_estado(pk, activar=False)

    def _cambiar_estado(self, pk, activar):
        servicio = _servicio()
        if activar:
            tipo = servicio.activar_tipo_producto(pk)
        else:
            tipo = servicio.desactivar_tipo_producto(pk)
        return Response(TipoProductoSerializer(tipo).data)
