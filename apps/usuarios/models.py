"""Modelos ORM Django para usuarios."""

import uuid
from typing import ClassVar

from django.db import models


class RolModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(default="")

    class Meta:
        db_table = "roles"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(
                models.functions.Lower("nombre"),
                name="rol_nombre_unico_ci",
            )
        ]


class UsuarioModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=120)
    email = models.EmailField(max_length=160, unique=True)
    rol = models.ForeignKey(RolModel, on_delete=models.PROTECT)
    estado = models.CharField(max_length=30, default="activo")
    username = models.CharField(max_length=120, unique=True, default="")
    password_hash = models.CharField(max_length=255, default="")
    creado_por = models.CharField(max_length=36, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuarios"
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["estado"], name="usuario_estado_idx"),
        ]


class SesionModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    usuario = models.ForeignKey(UsuarioModel, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    ip = models.CharField(max_length=60, default="")
    estado = models.CharField(max_length=30, default="activa")

    class Meta:
        db_table = "sesiones"
        indexes: ClassVar[list[object]] = [
            models.Index(
                fields=["usuario", "estado"],
                name="sesion_usuario_estado_idx",
            ),
            models.Index(fields=["fecha_expiracion"], name="sesion_expira_idx"),
        ]


class IntentoLoginModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=120)
    fecha = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=60, default="")
    exitoso = models.BooleanField(default=False)
    motivo_fallo = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        db_table = "intentos_login"
        indexes: ClassVar[list[object]] = [
            models.Index(
                fields=["username", "fecha"],
                name="intento_usuario_fecha_idx",
            ),
        ]
