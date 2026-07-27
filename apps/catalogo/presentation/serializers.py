"""Serializers DRF para catalogo."""

from decimal import Decimal
from typing import ClassVar

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.catalogo.infrastructure.models import PrendaModel, VariantePrendaModel


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


class VarianteCatalogoSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    prenda_id = serializers.PrimaryKeyRelatedField(
        source="prenda",
        queryset=PrendaModel.objects.all(),
        pk_field=serializers.UUIDField(format="hex_verbose"),
    )
    precio_efectivo = serializers.SerializerMethodField()
    moneda = serializers.SerializerMethodField()
    stock_disponible = serializers.SerializerMethodField()

    class Meta:
        model = VariantePrendaModel
        fields: ClassVar[list[str]] = [
            "id",
            "prenda_id",
            "sku",
            "talla",
            "color",
            "activa",
            "precio_monto",
            "precio_moneda",
            "precio_efectivo",
            "moneda",
            "stock_disponible",
        ]
        read_only_fields: ClassVar[list[str]] = [
            "id",
            "precio_efectivo",
            "moneda",
            "stock_disponible",
        ]

    def validate(self, attrs):
        monto = attrs.get(
            "precio_monto",
            self.instance.precio_monto if self.instance else None,
        )
        moneda = attrs.get(
            "precio_moneda",
            self.instance.precio_moneda if self.instance else None,
        )
        if (monto is None) != (moneda is None):
            raise serializers.ValidationError(
                "El precio propio requiere monto y moneda; omita ambos para heredarlo."
            )
        return attrs

    @staticmethod
    def get_precio_efectivo(obj):
        monto = obj.precio_monto
        if monto is None:
            monto = obj.prenda.precio_monto
        return f"{monto:.2f}"

    @staticmethod
    def get_moneda(obj):
        return obj.precio_moneda or obj.prenda.precio_moneda

    @staticmethod
    def get_stock_disponible(obj):
        try:
            stock = obj.stock
        except ObjectDoesNotExist:
            return None
        return stock.cantidad_actual - stock.cantidad_reservada


class PrendaSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    categoria_id = serializers.CharField(read_only=True)
    tipo_producto_id = serializers.CharField(read_only=True, allow_null=True)
    registrado_por = serializers.CharField(
        source="registrado_por_id",
        read_only=True,
        allow_null=True,
    )
    tallas = serializers.SerializerMethodField()
    variantes = VarianteCatalogoSerializer(many=True, read_only=True)

    class Meta:
        model = PrendaModel
        fields: ClassVar[list[str]] = [
            "id",
            "nombre",
            "descripcion",
            "precio_monto",
            "precio_moneda",
            "categoria_id",
            "tipo_producto_id",
            "tallas",
            "estado",
            "imagen",
            "variantes",
            "registrado_por",
            "fecha_registro",
        ]
        read_only_fields: ClassVar[list[str]] = fields

    @staticmethod
    def get_tallas(obj):
        return [variante.talla for variante in obj.variantes.all()]


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
    tallas = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )
    estado = serializers.CharField(read_only=True)


class BuscarPrendasSerializer(serializers.Serializer):
    texto = serializers.CharField(
        required=False,
        allow_blank=True,
        trim_whitespace=True,
    )
    categoria_id = serializers.CharField(
        max_length=36,
        required=False,
        allow_blank=True,
    )
    tipo_producto_id = serializers.CharField(
        max_length=36,
        required=False,
        allow_blank=True,
    )
    estado = serializers.ChoiceField(
        choices=["activa", "inactiva"],
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        desconocidos = set(self.initial_data) - set(self.fields)
        if desconocidos:
            raise serializers.ValidationError(
                "Parametros de consulta no permitidos: "
                f"{', '.join(sorted(desconocidos))}"
            )
        return attrs


class FiltrarVariantesSerializer(serializers.Serializer):
    prenda_id = serializers.UUIDField(required=False)
    activa = serializers.BooleanField(required=False)

    def validate(self, attrs):
        desconocidos = set(self.initial_data) - set(self.fields)
        if desconocidos:
            raise serializers.ValidationError(
                "Parametros de consulta no permitidos: "
                f"{', '.join(sorted(desconocidos))}"
            )
        return attrs


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
    tallas = serializers.ListField(
        child=serializers.CharField(max_length=20, trim_whitespace=True),
        required=False,
        default=list,
    )
    imagen = serializers.ImageField(
        required=False,
        allow_null=True,
    )


class ActualizarPrendaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120, trim_whitespace=True)
    descripcion = serializers.CharField(allow_blank=True, trim_whitespace=True)
    precio_monto = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
    precio_moneda = serializers.RegexField(r"^[A-Za-z]{3}$")
    categoria_id = serializers.CharField(max_length=36)
    tipo_producto_id = serializers.CharField(
        max_length=36,
        allow_null=True,
    )
    imagen = serializers.ImageField(required=False, allow_null=True)


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
    tallas = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )
    estado = serializers.CharField(read_only=True)
    registrado_por = serializers.CharField(read_only=True, allow_null=True)
    fecha_registro = serializers.DateTimeField(read_only=True)
