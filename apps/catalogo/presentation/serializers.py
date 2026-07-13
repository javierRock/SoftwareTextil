"""Serializers DRF para catalogo."""

from rest_framework import serializers

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel, TipoProductoModel


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaModel
        fields = ["id", "nombre", "descripcion"]


class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProductoModel
        fields = ["id", "nombre", "atributos_base"]


class PrendaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)

    class Meta:
        model = PrendaModel
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio_monto",
            "precio_moneda",
            "categoria",
            "categoria_nombre",
            "tipo_producto",
            "estado",
            "registrado_por",
            "fecha_registro",
        ]


class CrearPrendaSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    descripcion = serializers.CharField(required=False, default="")
    precio_monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    precio_moneda = serializers.CharField(required=False, default="PEN")
    categoria_id = serializers.CharField()
    tipo_producto_id = serializers.CharField(required=False, allow_null=True)
    registrado_por = serializers.CharField(required=False, allow_null=True)
