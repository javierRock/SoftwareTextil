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
        fields = ["id", "nombre", "email", "username", "estado", "rol", "rol_nombre", "fecha_creacion"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class CrearUsuarioSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    email = serializers.EmailField()
    rol_id = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
