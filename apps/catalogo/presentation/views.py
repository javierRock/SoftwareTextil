"""Views DRF para catalogo."""

from typing import ClassVar

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Prefetch, Q
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.response import Response

from apps.catalogo.application.services import ServicioCatalogo
from apps.catalogo.domain.excepciones import RecursoNoEncontradoError
from apps.catalogo.infrastructure.models import PrendaModel, VariantePrendaModel
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
    FiltrarVariantesSerializer,
    PrendaSerializer,
    TipoProductoSerializer,
    VarianteCatalogoSerializer,
)
from apps.compartido.domain.enums import EstadoPrenda
from apps.usuarios.presentation.permissions import EsAdministrador


def _servicio() -> ServicioCatalogo:
    return ServicioCatalogo(DjangoRepositorioPrenda(), DjangoRepositorioCatalogo())


def _es_administrador(request) -> bool:
    usuario = getattr(request, "user", None)
    rol = getattr(usuario, "rol", "")
    nombre_rol = rol if isinstance(rol, str) else getattr(rol, "nombre", "")
    return bool(
        usuario
        and usuario.is_authenticated
        and nombre_rol.casefold() == "administrador"
    )


class LecturaPublicaEscrituraAdministradorMixin:
    def get_permissions(self):
        clases = (
            [AllowAny]
            if self.request.method in SAFE_METHODS
            else [EsAdministrador]
        )
        return [clase() for clase in clases]


class PrendaViewSet(
    LecturaPublicaEscrituraAdministradorMixin,
    ManejoErroresCatalogoMixin,
    viewsets.ModelViewSet,
):
    queryset = PrendaModel.objects.all()
    serializer_class = PrendaSerializer
    http_method_names: ClassVar[list[str]] = [
        "get",
        "post",
        "put",
        "patch",
        "head",
        "options",
    ]

    def get_queryset(self):
        variantes = VariantePrendaModel.objects.select_related("prenda", "stock")
        prendas = PrendaModel.objects.select_related(
            "categoria",
            "tipo_producto",
        )
        if not _es_administrador(self.request):
            prendas = prendas.filter(estado=EstadoPrenda.ACTIVA.value)
            variantes = variantes.filter(activa=True)
        return prendas.prefetch_related(
            Prefetch("variantes", queryset=variantes),
        )

    def list(self, request, *args, **kwargs):
        parametros = BuscarPrendasSerializer(data=request.query_params)
        parametros.is_valid(raise_exception=True)
        datos = parametros.validated_data
        prendas = self.get_queryset()
        if not _es_administrador(request):
            encontradas = _servicio().buscar_prendas(**datos)
            prendas = prendas.filter(id__in=[prenda.id for prenda in encontradas])
        if datos.get("texto"):
            texto = datos["texto"]
            prendas = prendas.filter(
                Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)
            )
        if datos.get("categoria_id"):
            prendas = prendas.filter(categoria_id=datos["categoria_id"])
        if datos.get("tipo_producto_id"):
            prendas = prendas.filter(tipo_producto_id=datos["tipo_producto_id"])
        if datos.get("estado"):
            prendas = prendas.filter(estado=datos["estado"])
        return Response(self.get_serializer(prendas, many=True).data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        prenda_dominio = _servicio().buscar_prenda(pk)
        if (
            not _es_administrador(request)
            and prenda_dominio.estado != EstadoPrenda.ACTIVA
        ):
            raise RecursoNoEncontradoError("Prenda no encontrada")
        prenda = self.get_queryset().get(id=prenda_dominio.id)
        return Response(self.get_serializer(prenda).data)

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
            registrado_por=str(request.user.id),
            tipo_producto_id=serializer.validated_data.get("tipo_producto_id"),
            tallas=serializer.validated_data["tallas"],
        )
        model = self.get_queryset().get(id=prenda.id)
        if "imagen" in serializer.validated_data:
            model.imagen = serializer.validated_data["imagen"]
            model.save(update_fields=["imagen"])
        return Response(self.get_serializer(model).data, status=status.HTTP_201_CREATED)

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
        model = self.get_queryset().get(id=prenda.id)
        if "imagen" in datos:
            model.imagen = datos["imagen"]
            model.save(update_fields=["imagen"])
        return Response(self.get_serializer(model).data)

    @action(detail=True, methods=["post"], url_path="activar")
    def activar(self, request, pk=None):
        prenda = _servicio().activar_prenda(pk)
        model = self.get_queryset().get(id=prenda.id)
        return Response(self.get_serializer(model).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        prenda = _servicio().desactivar_prenda(pk)
        model = self.get_queryset().get(id=prenda.id)
        return Response(self.get_serializer(model).data, status=status.HTTP_200_OK)


class VarianteViewSet(
    LecturaPublicaEscrituraAdministradorMixin,
    viewsets.ModelViewSet,
):
    serializer_class = VarianteCatalogoSerializer
    http_method_names: ClassVar[list[str]] = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        variantes = VariantePrendaModel.objects.select_related("prenda", "stock")
        if not _es_administrador(self.request):
            variantes = variantes.filter(
                activa=True,
                prenda__estado=EstadoPrenda.ACTIVA.value,
            )
        filtros = getattr(self, "filtros_validados", {})
        prenda_id = filtros.get("prenda_id")
        activa = filtros.get("activa")
        if prenda_id:
            variantes = variantes.filter(prenda_id=prenda_id)
        if activa is not None:
            variantes = variantes.filter(activa=activa)
        return variantes.order_by("talla", "color")

    def list(self, request, *args, **kwargs):
        filtros = FiltrarVariantesSerializer(data=request.query_params)
        filtros.is_valid(raise_exception=True)
        self.filtros_validados = filtros.validated_data
        return super().list(request, *args, **kwargs)

    def get_object(self):
        try:
            return super().get_object()
        except DjangoValidationError as exc:
            raise Http404 from exc


class CategoriaViewSet(
    LecturaPublicaEscrituraAdministradorMixin,
    ManejoErroresCatalogoMixin,
    viewsets.ViewSet,
):
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
        return Response(
            CategoriaSerializer(categoria).data,
            status=status.HTTP_201_CREATED,
        )

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


class TipoProductoViewSet(
    LecturaPublicaEscrituraAdministradorMixin,
    ManejoErroresCatalogoMixin,
    viewsets.ViewSet,
):
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
        return Response(
            TipoProductoSerializer(tipo).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=False)

    def partial_update(self, request, pk=None):
        return self._actualizar(request, pk, parcial=True)

    def _actualizar(self, request, pk, parcial):
        servicio = _servicio()
        actual = servicio.buscar_tipo(pk)

        serializer = ActualizarTipoProductoSerializer(
            data=request.data,
            partial=parcial,
        )
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
