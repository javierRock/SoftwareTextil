"""Serializers DRF para carrito de compras.

Serializan el agregado de dominio, no el modelo del ORM: asi la presentacion
depende de la abstraccion del dominio y no de la tecnologia de persistencia
(DIP). Los serializers de entrada solo validan el contrato HTTP.
"""

from rest_framework import serializers


class ItemCarritoSerializer(serializers.Serializer):
    """Representacion de salida de `ItemCarrito`."""

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


class CarritoSerializer(serializers.Serializer):
    """Representacion de salida de `CarritoCompras`."""

    id = serializers.CharField(read_only=True)
    cliente_id = serializers.CharField(read_only=True)
    estado = serializers.CharField(source="estado.value", read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    items = ItemCarritoSerializer(many=True, read_only=True)


class CrearCarritoSerializer(serializers.Serializer):
    """El cliente siempre se toma de la sesion autenticada."""


class AgregarItemSerializer(serializers.Serializer):
    variante_id = serializers.CharField()
    cantidad = serializers.IntegerField(min_value=1)
    # Compatibilidad de entrada: se aceptan pero el backend nunca los utiliza.
    precio_monto = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, write_only=True
    )
    precio_moneda = serializers.CharField(required=False, write_only=True)


class QuitarItemSerializer(serializers.Serializer):
    variante_id = serializers.CharField()
