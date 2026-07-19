"""Views DRF para carrito de compras."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.ventas.carrito.application.services import ServicioCompras
from apps.ventas.carrito.infrastructure.models import CarritoModel
from apps.ventas.carrito.infrastructure.repositories import DjangoRepositorioCarrito
from apps.ventas.carrito.presentation.serializers import (
    AgregarItemSerializer,
    CarritoSerializer,
    CrearCarritoSerializer,
    QuitarItemSerializer,
)


def _servicio() -> ServicioCompras:
    return ServicioCompras(DjangoRepositorioCarrito())


class CarritoViewSet(viewsets.ViewSet):
    def list(self, request):
        cliente_id = request.query_params.get("cliente_id")
        if cliente_id:
            carritos = CarritoModel.objects.filter(cliente_id=cliente_id)
        else:
            carritos = CarritoModel.objects.all()
        return Response(CarritoSerializer(carritos, many=True).data)

    def create(self, request):
        serializer = CrearCarritoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        carrito = _servicio().crear_carrito(cliente_id=serializer.validated_data["cliente_id"])
        return Response({"id": carrito.id, "cliente_id": carrito.cliente_id, "estado": carrito.estado.value}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            carrito = _servicio().obtener_carrito(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        model = CarritoModel.objects.get(id=carrito.id)
        return Response(CarritoSerializer(model).data)

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
        servicio = _servicio()
        try:
            carrito = servicio.agregar_item(
                carrito_id=pk,
                prenda_id=serializer.validated_data["prenda_id"],
                cantidad=serializer.validated_data["cantidad"],
                precio_monto=serializer.validated_data["precio_monto"],
                precio_moneda=serializer.validated_data["precio_moneda"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        model = CarritoModel.objects.get(id=carrito.id)
        return Response(CarritoSerializer(model).data, status=status.HTTP_201_CREATED)

    def _quitar_item(self, request, pk):
        serializer = QuitarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio()
        try:
            carrito = servicio.quitar_item(pk, serializer.validated_data["prenda_id"])
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        model = CarritoModel.objects.get(id=carrito.id)
        return Response(CarritoSerializer(model).data, status=status.HTTP_200_OK)
