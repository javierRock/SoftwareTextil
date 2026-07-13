"""Serializers DRF para inventario."""

from rest_framework import serializers

from apps.inventario.infrastructure.models import (
    AlertaStockModel,
    MovimientoInventarioModel,
    StockPrendaModel,
)


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrendaModel
        fields = [
            "id",
            "prenda_id",
            "cantidad_actual",
            "nivel_minimo",
            "ubicacion",
            "unidad",
            "ultima_actualizacion",
        ]


class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventarioModel
        fields = ["id", "stock", "tipo", "cantidad", "motivo", "registrado_por", "fecha"]


class AlertaStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaStockModel
        fields = ["id", "stock", "nivel_actual", "nivel_minimo", "estado", "fecha"]


class CrearStockSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
    stock_inicial = serializers.IntegerField()
    stock_minimo = serializers.IntegerField()
    ubicacion = serializers.CharField(required=False, default="almacen")


class MovimientoStockSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
    cantidad = serializers.IntegerField()
    motivo = serializers.CharField()
    usuario_id = serializers.CharField()


class AjusteStockSerializer(serializers.Serializer):
    prenda_id = serializers.CharField()
    nueva_cantidad = serializers.IntegerField()
    motivo = serializers.CharField()
    usuario_id = serializers.CharField()
