"""Serializers DRF para inventario."""

from typing import ClassVar

from rest_framework import serializers

from apps.inventario.infrastructure.models import (
    AlertaStockModel,
    MovimientoInventarioModel,
    StockVarianteModel,
)


class StockSerializer(serializers.ModelSerializer):
    cantidad_disponible = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockVarianteModel
        fields: ClassVar[list[str]] = [
            "id",
            "variante_id",
            "cantidad_actual",
            "cantidad_reservada",
            "cantidad_disponible",
            "nivel_minimo",
            "ubicacion",
            "unidad",
            "ultima_actualizacion",
        ]


class MovimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventarioModel
        fields: ClassVar[list[str]] = [
            "id",
            "stock",
            "tipo",
            "cantidad",
            "motivo",
            "registrado_por",
            "fecha",
        ]


class AlertaStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaStockModel
        fields: ClassVar[list[str]] = [
            "id",
            "stock",
            "nivel_actual",
            "nivel_minimo",
            "estado",
            "fecha",
        ]


class CrearStockSerializer(serializers.Serializer):
    variante_id = serializers.UUIDField()
    stock_inicial = serializers.IntegerField(min_value=0)
    stock_minimo = serializers.IntegerField(min_value=0)
    ubicacion = serializers.CharField(
        required=False,
        default="almacen",
    )


class MovimientoStockSerializer(serializers.Serializer):
    variante_id = serializers.UUIDField()
    cantidad = serializers.IntegerField(min_value=1)
    motivo = serializers.CharField()
    usuario_id = serializers.UUIDField()


class AjusteStockSerializer(serializers.Serializer):
    variante_id = serializers.UUIDField()
    nueva_cantidad = serializers.IntegerField(min_value=0)
    motivo = serializers.CharField()
    usuario_id = serializers.UUIDField()
