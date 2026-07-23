"""Serializers DRF para inventario."""

from rest_framework import serializers

from apps.inventario.infrastructure.models import (
    AlertaStockModel,
)


class StockSerializer(serializers.Serializer):
    id = serializers.CharField()
    prenda_id = serializers.CharField()
    cantidad_actual = serializers.IntegerField()
    nivel_minimo = serializers.IntegerField()
    ubicacion = serializers.CharField()
    unidad = serializers.CharField()
    ultima_actualizacion = serializers.DateTimeField()


class MovimientoSerializer(serializers.Serializer):
    id = serializers.CharField()
    stock_id = serializers.CharField()
    tipo = serializers.CharField()
    cantidad = serializers.IntegerField()
    motivo = serializers.CharField()
    registrado_por = serializers.CharField()
    fecha = serializers.DateTimeField()


class AlertaStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaStockModel
        fields = ["id", "stock", "nivel_actual", "nivel_minimo", "estado", "fecha"]


class CrearStockSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
    stock_inicial = serializers.IntegerField(min_value=0)
    stock_minimo = serializers.IntegerField(min_value=0)
    ubicacion = serializers.CharField(required=False, default="almacen")


class MovimientoStockSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
    cantidad = serializers.IntegerField(min_value=1)
    motivo = serializers.CharField()
    usuario_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AjusteStockSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
    nueva_cantidad = serializers.IntegerField(min_value=0)
    motivo = serializers.CharField()
    usuario_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
