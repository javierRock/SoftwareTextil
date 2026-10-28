"""Modelos ORM Django para usuarios."""

from typing import ClassVar

from django.db import models
from django.db.models.functions import Lower

from apps.compartido.domain.enums import EstadoSesion, EstadoUsuario
from apps.compartido.infrastructure.campos import campo_estado, check_enum
from apps.compartido.infrastructure.models import ModeloBase

ALGORITMO_HASH_POR_DEFECTO = "werkzeug-pbkdf2"


class PermisoModel(ModeloBase):
    """Permiso atomico que un rol puede otorgar sobre un modulo."""

    codigo = models.CharField(max_length=120, unique=True)
    descripcion = models.TextField(default="")
    modulo = models.CharField(max_length=60)

    class Meta:
        db_table = "permisos"
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["modulo"], name="permiso_modulo_idx"),
        ]


class RolModel(ModeloBase):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(default="")
    permisos = models.ManyToManyField(
        PermisoModel,
        through="RolPermisoModel",
        related_name="roles",
    )

    class Meta:
        db_table = "roles"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(
                Lower("nombre"),
                name="rol_nombre_unico_ci",
            ),
        ]


class RolPermisoModel(ModeloBase):
    """Tabla intermedia explicita entre roles y permisos."""

    rol = models.ForeignKey(
        RolModel,
        on_delete=models.CASCADE,
        related_name="asignaciones",
    )
    permiso = models.ForeignKey(
        PermisoModel,
        on_delete=models.CASCADE,
        related_name="asignaciones",
    )

    class Meta:
        db_table = "roles_permisos"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(
                fields=["rol", "permiso"],
                name="rol_permiso_unico",
            ),
        ]


class UsuarioModel(ModeloBase):
    """Raiz del agregado Usuario, con la credencial embebida como columnas."""

    nombre = models.CharField(max_length=120)
    email = models.EmailField(max_length=160)
    username = models.CharField(max_length=120)
    rol = models.ForeignKey(
        RolModel,
        on_delete=models.PROTECT,
        related_name="usuarios",
    )
    estado = campo_estado(EstadoUsuario, default=EstadoUsuario.ACTIVO)
    password_hash = models.CharField(max_length=255, default="")
    password_salt = models.CharField(max_length=64, default="")
    password_algoritmo = models.CharField(
        max_length=60,
        default=ALGORITMO_HASH_POR_DEFECTO,
    )
    password_actualizado_en = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios_creados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuarios"
        constraints: ClassVar[list[object]] = [
            # La busqueda es `email__iexact` y `username__iexact`, asi que la
            # unicidad tambien debe ignorar mayusculas: con `unique=True` a
            # secas se podian registrar "Ana" y "ana" como usuarios distintos.
            models.UniqueConstraint(Lower("email"), name="usuario_email_unico_ci"),
            models.UniqueConstraint(
                Lower("username"),
                name="usuario_username_unico_ci",
            ),
            check_enum("estado", EstadoUsuario, "usuario_estado_valido"),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["estado"], name="usuario_estado_idx"),
            models.Index(fields=["rol"], name="usuario_rol_idx"),
        ]


class SesionModel(ModeloBase):
    usuario = models.ForeignKey(
        UsuarioModel,
        on_delete=models.CASCADE,
        related_name="sesiones",
    )
    token = models.CharField(max_length=255, unique=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    estado = campo_estado(EstadoSesion, default=EstadoSesion.ACTIVA)

    class Meta:
        db_table = "sesiones"
        constraints: ClassVar[list[object]] = [
            check_enum("estado", EstadoSesion, "sesion_estado_valido"),
            models.CheckConstraint(
                condition=models.Q(fecha_expiracion__gt=models.F("fecha_inicio")),
                name="sesion_expiracion_posterior_al_inicio",
            ),
        ]
        indexes: ClassVar[list[object]] = [
            # Indice parcial: la autenticacion solo consulta sesiones activas,
            # que son una fraccion minima de la tabla historica.
            models.Index(
                fields=["usuario"],
                condition=models.Q(estado=EstadoSesion.ACTIVA.value),
                name="sesion_activa_usuario_idx",
            ),
            models.Index(fields=["fecha_expiracion"], name="sesion_expira_idx"),
        ]


class IntentoLoginModel(ModeloBase):
    username = models.CharField(max_length=120)
    fecha = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    exitoso = models.BooleanField(default=False)
    motivo_fallo = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        db_table = "intentos_login"
        indexes: ClassVar[list[object]] = [
            models.Index(
                fields=["username", "-fecha"],
                name="intento_usuario_fecha_idx",
            ),
        ]
