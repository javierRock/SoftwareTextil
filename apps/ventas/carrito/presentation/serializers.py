"""Serializers DRF para carrito de compras."""

from rest_framework import serializers

from apps.ventas.carrito.infrastructure.models import CarritoModel, ItemCarritoModel


class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarritoModel
        fields = ["id", "prenda_id", "cantidad", "precio_monto", "precio_moneda"]


class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)

    class Meta:
        model = CarritoModel
        fields = ["id", "cliente_id", "estado", "fecha_creacion", "items"]


class CrearCarritoSerializer(serializers.Serializer):
    cliente_id = serializers.CharField()


class AgregarItemSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
    cantidad = serializers.IntegerField(min_value=1)
    precio_monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    precio_moneda = serializers.CharField(required=False, default="PEN")


class QuitarItemSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
