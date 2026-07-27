"""Views DRF para carrito de compras.

La vista tiene una sola responsabilidad (SRP): traducir HTTP a casos de uso y
el resultado a una respuesta. No consulta el ORM ni instancia repositorios
concretos; los recibe de las fabricas del modulo a traves de atributos de
clase, que las pruebas pueden reemplazar por dobles en memoria (DIP).
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ventas.carrito.domain.errors import CarritoError
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


class CarritoViewSet(viewsets.ViewSet):
    construir_servicio = staticmethod(construir_servicio_compras)
    construir_consulta = staticmethod(construir_consulta_carritos)

    def list(self, request):
        cliente_id = request.query_params.get("cliente_id")
        carritos = self.construir_consulta().listar(cliente_id)
        return Response(CarritoSerializer(carritos, many=True).data)

    def create(self, request):
        serializer = CrearCarritoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carrito = self.construir_servicio().crear_carrito(
            cliente_id=serializer.validated_data["cliente_id"]
        )
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            carrito = self.construir_consulta().obtener(pk)
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
        serializer.is_valid(raise_exception=True)
        try:
            carrito = self.construir_servicio().agregar_item(
                carrito_id=pk,
                prenda_id=serializer.validated_data["prenda_id"],
                cantidad=serializer.validated_data["cantidad"],
                precio_monto=serializer.validated_data["precio_monto"],
                precio_moneda=serializer.validated_data["precio_moneda"],
            )
        except CarritoError as exc:
            return respuesta_de_error_carrito(exc)
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_201_CREATED)

    def _quitar_item(self, request, pk):
        serializer = QuitarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            carrito = self.construir_servicio().quitar_item(
                pk, serializer.validated_data["prenda_id"]
            )
        except CarritoError as exc:
            return respuesta_de_error_carrito(exc)
        return Response(CarritoSerializer(carrito).data, status=status.HTTP_200_OK)
