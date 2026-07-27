"""Serializers DRF para catalogo."""

from decimal import Decimal

from rest_framework import serializers

from apps.catalogo.infrastructure.models import PrendaModel


class CrearCategoriaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120, trim_whitespace=True)
    descripcion = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        trim_whitespace=True,
    )


class ActualizarCategoriaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120, trim_whitespace=True)
    descripcion = serializers.CharField(allow_blank=True, trim_whitespace=True)


class CategoriaSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    descripcion = serializers.CharField(read_only=True)


class CrearTipoProductoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120, trim_whitespace=True)
    atributos_base = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        default=dict,
    )


class ActualizarTipoProductoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120, trim_whitespace=True)
    atributos_base = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
    )


class TipoProductoSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    atributos_base = serializers.DictField(read_only=True)
    activo = serializers.BooleanField(read_only=True)


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


class PrendaCatalogoSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    descripcion = serializers.CharField(read_only=True)
    precio_monto = serializers.DecimalField(
        source="precio.monto",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    precio_moneda = serializers.CharField(source="precio.moneda", read_only=True)
    categoria_id = serializers.CharField(read_only=True)
    tipo_producto_id = serializers.CharField(read_only=True, allow_null=True)
    estado = serializers.CharField(read_only=True)


class CrearPrendaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120, trim_whitespace=True)
    descripcion = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        trim_whitespace=True,
    )
    precio_monto = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    precio_moneda = serializers.RegexField(
        r"^[A-Za-z]{3}$",
        required=False,
        default="PEN",
    )
    categoria_id = serializers.CharField(max_length=36)
    tipo_producto_id = serializers.CharField(
        max_length=36,
        required=False,
        allow_null=True,
    )
    registrado_por = serializers.CharField(
        max_length=36,
        required=False,
        allow_null=True,
    )


class PrendaCreadaSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    descripcion = serializers.CharField(read_only=True)
    precio_monto = serializers.DecimalField(
        source="precio.monto",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    precio_moneda = serializers.CharField(source="precio.moneda", read_only=True)
    categoria_id = serializers.CharField(read_only=True)
    tipo_producto_id = serializers.CharField(read_only=True, allow_null=True)
    estado = serializers.CharField(read_only=True)
    registrado_por = serializers.CharField(read_only=True, allow_null=True)
    fecha_registro = serializers.DateTimeField(read_only=True)
