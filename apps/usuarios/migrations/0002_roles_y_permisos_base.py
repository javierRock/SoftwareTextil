"""Carga los roles y permisos base del sistema.

Se ejecuta como migracion de datos para que cualquier integrante obtenga la
misma matriz de autorizacion al levantar su base local.
"""

from typing import ClassVar
from uuid import uuid4

from django.db import migrations

ROLES_BASE = (
    ("Administrador", "Gestion completa de usuarios y configuracion"),
    ("Cliente", "Acceso de cliente al sistema de comercio textil"),
    ("Encargado de inventario", "Control de stock, movimientos y despachos"),
)

# (codigo, descripcion, modulo)
PERMISOS_BASE = (
    ("usuarios.gestionar", "Crear, editar y desactivar usuarios", "usuarios"),
    ("catalogo.publicar", "Registrar y publicar prendas", "catalogo"),
    ("inventario.movimientos", "Registrar ingresos, salidas y ajustes", "inventario"),
    ("ventas.pedidos", "Consultar y gestionar pedidos", "ventas"),
    ("ventas.pagos", "Aprobar o rechazar pagos", "ventas"),
    ("ventas.despachos", "Preparar y confirmar despachos", "ventas"),
)

PERMISOS_POR_ROL = {
    "Administrador": [codigo for codigo, _, _ in PERMISOS_BASE],
    "Cliente": [],
    "Encargado de inventario": [
        "inventario.movimientos",
        "ventas.despachos",
    ],
}


def cargar_datos_base(apps, schema_editor):
    rol_model = apps.get_model("usuarios", "RolModel")
    permiso_model = apps.get_model("usuarios", "PermisoModel")
    rol_permiso_model = apps.get_model("usuarios", "RolPermisoModel")

    roles = {}
    for nombre, descripcion in ROLES_BASE:
        rol, _ = rol_model.objects.get_or_create(
            nombre=nombre,
            defaults={"id": uuid4(), "descripcion": descripcion},
        )
        roles[nombre] = rol

    permisos = {}
    for codigo, descripcion, modulo in PERMISOS_BASE:
        permiso, _ = permiso_model.objects.get_or_create(
            codigo=codigo,
            defaults={"id": uuid4(), "descripcion": descripcion, "modulo": modulo},
        )
        permisos[codigo] = permiso

    for nombre_rol, codigos in PERMISOS_POR_ROL.items():
        for codigo in codigos:
            rol_permiso_model.objects.get_or_create(
                rol=roles[nombre_rol],
                permiso=permisos[codigo],
                defaults={"id": uuid4()},
            )


def revertir_datos_base(apps, schema_editor):
    apps.get_model("usuarios", "RolPermisoModel").objects.all().delete()
    apps.get_model("usuarios", "PermisoModel").objects.filter(
        codigo__in=[codigo for codigo, _, _ in PERMISOS_BASE]
    ).delete()
    apps.get_model("usuarios", "RolModel").objects.filter(
        nombre__in=[nombre for nombre, _ in ROLES_BASE]
    ).delete()


class Migration(migrations.Migration):
    dependencies: ClassVar[list[tuple[str, str]]] = [("usuarios", "0001_initial")]

    operations: ClassVar[list[object]] = [
        migrations.RunPython(cargar_datos_base, revertir_datos_base),
    ]
