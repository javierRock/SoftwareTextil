"""Serializers DRF para pagos."""

from rest_framework import serializers

DATOS_SENSIBLES_PROHIBIDOS = frozenset(
    {
        "card_number",
        "cvv",
        "numero_tarjeta",
        "pin",
    }
)


class CrearPagoSerializer(serializers.Serializer):
    """Valida la estructura de una solicitud de registro de pago."""

    pedido_id = serializers.CharField(allow_blank=False, trim_whitespace=True)
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo = serializers.CharField(allow_blank=False, trim_whitespace=True)
    referencia = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        trim_whitespace=True,
        max_length=120,
    )

    def validate(self, atributos: dict[str, object]) -> dict[str, object]:
        campos_recibidos = set(self.initial_data)
        if campos_recibidos & DATOS_SENSIBLES_PROHIBIDOS:
            raise serializers.ValidationError(
                "No se aceptan datos sensibles de medios de pago."
            )
        return atributos


class FiltroPagosSerializer(serializers.Serializer):
    """Valida los parametros opcionales del listado."""

    pedido_id = serializers.CharField(
        required=False,
        allow_blank=False,
        trim_whitespace=True,
    )


class PagoSerializer(serializers.Serializer):
    """Serializa agregados Pago sin exponer modelos de infraestructura."""

    id = serializers.CharField(read_only=True)
    pedido_id = serializers.CharField(read_only=True)
    monto_monto = serializers.DecimalField(
        source="monto.monto",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    monto_moneda = serializers.CharField(source="monto.moneda", read_only=True)
    metodo = serializers.CharField(read_only=True)
    referencia = serializers.CharField(read_only=True)
    estado = serializers.CharField(read_only=True)
    fecha = serializers.DateTimeField(read_only=True)
