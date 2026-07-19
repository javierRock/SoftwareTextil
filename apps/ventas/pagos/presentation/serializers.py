"""Serializers DRF para pagos."""

from rest_framework import serializers

from apps.ventas.pagos.infrastructure.models import PagoModel


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoModel
        fields = ["id", "pedido_id", "monto_monto", "monto_moneda", "metodo", "referencia", "estado", "fecha"]


class CrearPagoSerializer(serializers.Serializer):
    pedido_id = serializers.CharField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo = serializers.CharField()
    referencia = serializers.CharField(required=False, default="")
