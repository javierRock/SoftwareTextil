"""Serializers DRF para pedidos."""

from rest_framework import serializers

from apps.ventas.pedidos.infrastructure.models import DetallePedidoModel, PedidoModel


class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedidoModel
        fields = ["id", "prenda_id", "cantidad", "precio_monto", "precio_moneda"]


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = PedidoModel
        fields = ["id", "cliente_id", "carrito_id", "total_monto", "total_moneda", "estado", "fecha_creacion", "detalles"]


class CrearPedidoSerializer(serializers.Serializer):
    carrito_id = serializers.CharField()
    cliente_id = serializers.CharField()
