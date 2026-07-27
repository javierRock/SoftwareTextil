"""Serializers DRF para inventario.

Proyectan los objetos del dominio, no los modelos ORM: la capa de presentacion
no deberia conocer la forma de las tablas.
"""

from rest_framework import serializers


class StockSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    variante_id = serializers.CharField(read_only=True)
    cantidad_actual = serializers.IntegerField(read_only=True)
    cantidad_reservada = serializers.IntegerField(read_only=True)
    cantidad_disponible = serializers.IntegerField(read_only=True)
    nivel_minimo = serializers.IntegerField(read_only=True)
    ubicacion = serializers.CharField(read_only=True)
    unidad = serializers.CharField(read_only=True)
    ultima_actualizacion = serializers.DateTimeField(read_only=True)


class MovimientoSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    stock_id = serializers.CharField(read_only=True)
    tipo = serializers.CharField(read_only=True)
    cantidad = serializers.IntegerField(read_only=True)
    motivo = serializers.CharField(read_only=True)
    registrado_por = serializers.CharField(read_only=True)
    fecha = serializers.DateTimeField(read_only=True)


class AlertaStockSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    stock_id = serializers.CharField(read_only=True)
    nivel_actual = serializers.IntegerField(read_only=True)
    nivel_minimo = serializers.IntegerField(read_only=True)
    estado = serializers.CharField(read_only=True)
    fecha = serializers.DateTimeField(read_only=True)


class VarianteStockAgrupadaSerializer(serializers.Serializer):
    variante_id = serializers.CharField(read_only=True)
    sku = serializers.CharField(read_only=True)
    talla = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    cantidad = serializers.IntegerField(read_only=True)
    cantidad_reservada = serializers.IntegerField(read_only=True)
    cantidad_disponible = serializers.IntegerField(read_only=True)


class PrendaStockAgrupadaSerializer(serializers.Serializer):
    prenda_id = serializers.CharField(read_only=True)
    nombre = serializers.CharField(read_only=True)
    cantidad = serializers.IntegerField(read_only=True)
    variantes = VarianteStockAgrupadaSerializer(many=True, read_only=True)


class CategoriaStockAgrupadaSerializer(serializers.Serializer):
    """Resumen en tres niveles: categoria, sus prendas y sus variantes."""

    categoria_id = serializers.CharField(read_only=True)
    categoria = serializers.CharField(read_only=True)
    cantidad_total = serializers.IntegerField(read_only=True)
    prendas = PrendaStockAgrupadaSerializer(many=True, read_only=True)


class CrearStockSerializer(serializers.Serializer):
    variante_id = serializers.UUIDField()
    stock_inicial = serializers.IntegerField(min_value=0)
    stock_minimo = serializers.IntegerField(min_value=0)
    ubicacion = serializers.CharField(
        required=False,
        default="almacen",
        max_length=120,
    )


class MovimientoStockSerializer(serializers.Serializer):
    """El responsable sale de la sesion, nunca del cuerpo de la peticion."""

    variante_id = serializers.UUIDField()
    cantidad = serializers.IntegerField(min_value=1)
    motivo = serializers.CharField()


class AjusteStockSerializer(serializers.Serializer):
    variante_id = serializers.UUIDField()
    nueva_cantidad = serializers.IntegerField(min_value=0)
    motivo = serializers.CharField()
