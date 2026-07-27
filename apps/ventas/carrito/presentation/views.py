"""Views DRF para carrito de compras.

La vista tiene una sola responsabilidad (SRP): traducir HTTP a casos de uso y
el resultado a una respuesta. No consulta el ORM ni instancia repositorios
concretos; los recibe de las fabricas del modulo a traves de atributos de
clase, que las pruebas pueden reemplazar por dobles en memoria (DIP).
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from apps.usuarios.presentation.permissions import EsAdministrador, EsCliente
from apps.ventas.carrito.domain.errors import (
    CarritoError,
    CarritoNoPerteneceAClienteError,
)
from apps.ventas.carrito.infrastructure.factories import (
    construir_consulta_carritos,
    construir_servicio_compras,
)
from apps.ventas.carrito.presentation.errores import respuesta_de_error_carrito
from apps.ventas.carrito.presentation.serializers import (
    AgregarItemSerializer,
    CarritoSerializer,
    CrearCarritoSerializer,
    QuitarItemSerializer,
)
from apps.ventas.presentation.errores import respuesta_entrada_invalida


class CarritoViewSet(viewsets.ViewSet):
    construir_servicio = staticmethod(construir_servicio_compras)
    construir_consulta = staticmethod(construir_consulta_carritos)

    def get_permissions(self) -> list[BasePermission]:
        clases = [EsCliente | EsAdministrador]
        if self.action in {"create", "items"}:
            clases = [EsCliente]
        return [clase() for clase in clases]

    def list(self, request):
        cliente_id = str(request.user.id)
        if request.user.rol.casefold() == "administrador":
            cliente_id = request.query_params.get("cliente_id")
        carritos = self.construir_consulta().listar(cliente_id)
        return Response(CarritoSerializer(carritos, many=True).data)

    def create(self, request):
        serializer = CrearCarritoSerializer(data=request.data)
        if not serializer.is_valid():
            return respuesta_entrada_invalida(serializer.errors)
        carrito = self.construir_servicio().crear_carrito(
            cliente_id=str(request.user.id)
        )
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            carrito = self.construir_consulta().obtener(pk)
            if (
                request.user.rol.casefold() != "administrador"
                and carrito.cliente_id != str(request.user.id)
            ):
                raise CarritoNoPerteneceAClienteError
        except CarritoError as exc:
            return respuesta_de_error_carrito(exc)
        return Response(CarritoSerializer(carrito).data)

    @action(detail=True, methods=["post", "delete"], url_path="items")
    def items(self, request, pk=None):
        # Una sola ruta para items/: POST agrega, DELETE quita. Antes eran dos
        # acciones con el mismo url_path y el router solo enrutaba la primera.
        if request.method == "DELETE":
            return self._quitar_item(request, pk)
        return self._agregar_item(request, pk)

    def _agregar_item(self, request, pk):
        serializer = AgregarItemSerializer(data=request.data)
        if not serializer.is_valid():
            return respuesta_entrada_invalida(serializer.errors)
        try:
            carrito = self.construir_servicio().agregar_item(
                carrito_id=pk,
                variante_id=serializer.validated_data["variante_id"],
                cantidad=serializer.validated_data["cantidad"],
                cliente_id=str(request.user.id),
            )
        except CarritoError as exc:
            return respuesta_de_error_carrito(exc)
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_201_CREATED)

    def _quitar_item(self, request, pk):
        serializer = QuitarItemSerializer(data=request.data)
        if not serializer.is_valid():
            return respuesta_entrada_invalida(serializer.errors)
        try:
            carrito = self.construir_servicio().quitar_item(
                pk,
                serializer.validated_data["variante_id"],
                cliente_id=str(request.user.id),
            )
        except CarritoError as exc:
            return respuesta_de_error_carrito(exc)
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)
