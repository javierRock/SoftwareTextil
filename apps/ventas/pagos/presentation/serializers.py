"""Serializers DRF para pagos."""

from rest_framework import serializers

from apps.compartido.domain.enums import MetodoPago

TAMANO_PAGINA_PREDETERMINADO = 20
TAMANO_PAGINA_MAXIMO = 100


class SerializerEstricto(serializers.Serializer):
    """Rechaza claves desconocidas para no aceptar datos accidentalmente."""

    def validate(self, atributos: dict[str, object]) -> dict[str, object]:
        campos_desconocidos = set(self.initial_data) - set(self.fields)
        if campos_desconocidos:
            nombres = ", ".join(sorted(campos_desconocidos))
            raise serializers.ValidationError(f"Campos no permitidos: {nombres}.")
        return atributos


class CrearPagoSerializer(SerializerEstricto):
    """Valida la estructura de una solicitud de registro de pago."""

    pedido_id = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        max_length=36,
    )
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo = serializers.ChoiceField(
        choices=[metodo.value for metodo in MetodoPago],
    )
    referencia = serializers.CharField(
        required=False,
        default="",
        allow_blank=True,
        trim_whitespace=True,
        max_length=120,
    )


class FiltroPagosSerializer(SerializerEstricto):
    """Valida filtros y limites del listado paginado."""

    pedido_id = serializers.CharField(
        required=False,
        allow_blank=False,
        trim_whitespace=True,
        max_length=36,
    )
    pagina = serializers.IntegerField(required=False, default=1, min_value=1)
    tamano = serializers.IntegerField(
        required=False,
        default=TAMANO_PAGINA_PREDETERMINADO,
        min_value=1,
        max_value=TAMANO_PAGINA_MAXIMO,
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
