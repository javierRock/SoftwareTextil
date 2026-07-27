"""Serializers DRF para despachos."""

from rest_framework import serializers


class GuiaRemisionSerializer(serializers.Serializer):
    serie = serializers.CharField(max_length=10)
    numero = serializers.CharField(max_length=20)
    transportista = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        default="",
    )
    fecha_emision = serializers.DateTimeField(read_only=True)


class DespachoSerializer(serializers.Serializer):
    """Proyecta el agregado de dominio, no el modelo ORM."""

    id = serializers.CharField(read_only=True)
    pedido_id = serializers.CharField(read_only=True)
    direccion_entrega = serializers.CharField(read_only=True)
    estado = serializers.CharField(read_only=True)
    responsable_id = serializers.CharField(read_only=True, allow_null=True)
    guia = GuiaRemisionSerializer(read_only=True, allow_null=True)
    fecha_preparacion = serializers.DateTimeField(read_only=True, allow_null=True)
    fecha_confirmacion = serializers.DateTimeField(read_only=True, allow_null=True)


class ProgramarDespachoSerializer(serializers.Serializer):
    pedido_id = serializers.UUIDField()
    direccion_entrega = serializers.CharField(max_length=250)


class PrepararDespachoSerializer(serializers.Serializer):
    responsable_id = serializers.UUIDField()


class ConfirmarDespachoSerializer(GuiaRemisionSerializer):
    """Confirmar exige exactamente los datos de la guia de remision."""
