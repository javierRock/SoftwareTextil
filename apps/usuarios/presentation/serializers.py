"""Serializers DRF para usuarios."""

from rest_framework import serializers

from apps.usuarios.infrastructure.models import RolModel, UsuarioModel


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolModel
        fields = ["id", "nombre", "descripcion"]


class UsuarioSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source="rol.nombre", read_only=True)

    class Meta:
        model = UsuarioModel
        fields = [
            "id",
            "nombre",
            "email",
            "username",
            "estado",
            "rol",
            "rol_nombre",
            "fecha_creacion",
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=120, trim_whitespace=True)
    password = serializers.CharField(
        max_length=128,
        write_only=True,
        trim_whitespace=False,
    )


class CrearUsuarioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    rol_id = serializers.CharField()
    username = serializers.RegexField(
        r"^[a-zA-Z0-9._-]+$",
        max_length=120,
        error_messages={
            "invalid": "Usa solo letras, numeros, punto, guion o guion bajo."
        },
    )
    password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        trim_whitespace=False,
    )


class RegistroSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    username = serializers.RegexField(
        r"^[a-zA-Z0-9._-]+$",
        max_length=120,
        error_messages={
            "invalid": "Usa solo letras, numeros, punto, guion o guion bajo."
        },
    )
    password = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        trim_whitespace=False,
    )


class PerfilSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120)
    email = serializers.EmailField(max_length=160)


class CambiarPasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(
        max_length=128,
        write_only=True,
        trim_whitespace=False,
    )
    password_nuevo = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        trim_whitespace=False,
    )


class CrearRolSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120)
    descripcion = serializers.CharField(
        max_length=500,
        allow_blank=True,
        required=False,
    )
