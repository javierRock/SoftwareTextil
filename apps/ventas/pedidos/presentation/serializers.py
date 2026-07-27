"""Serializers DRF para pedidos.

Serializan el agregado de dominio, no el modelo del ORM: asi la presentacion
depende de la abstraccion del dominio y no de la tecnologia de persistencia
(DIP). Los serializers de entrada solo validan el contrato HTTP.
"""

from rest_framework import serializers


class DetallePedidoSerializer(serializers.Serializer):
    """Representacion de salida de `DetallePedido`."""

    id = serializers.CharField(read_only=True)
    variante_id = serializers.CharField(read_only=True)
    cantidad = serializers.IntegerField(read_only=True)
    precio_monto = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        source="precio_unitario.monto",
        read_only=True,
    )
    precio_moneda = serializers.CharField(
        source="precio_unitario.moneda", read_only=True
    )


class PedidoSerializer(serializers.Serializer):
    """Representacion de salida de `Pedido`."""

    id = serializers.CharField(read_only=True)
    cliente_id = serializers.CharField(read_only=True)
    carrito_id = serializers.CharField(read_only=True)
    total_monto = serializers.DecimalField(
        max_digits=12, decimal_places=2, source="total.monto", read_only=True
    )
    total_moneda = serializers.CharField(source="total.moneda", read_only=True)
    estado = serializers.CharField(source="estado.value", read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)


class CrearPedidoSerializer(serializers.Serializer):
    carrito_id = serializers.CharField()
    cliente_id = serializers.CharField()
