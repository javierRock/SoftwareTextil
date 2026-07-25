from django.db import migrations


ROLES_BASE = (
    ("Administrador", "Gestion completa de usuarios y configuracion"),
    ("Cliente", "Acceso de cliente al sistema de comercio textil"),
)


def crear_roles_base(apps, schema_editor):
    rol_model = apps.get_model("usuarios", "RolModel")
    for nombre, descripcion in ROLES_BASE:
        rol_model.objects.get_or_create(
            nombre=nombre,
            defaults={"descripcion": descripcion},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_intentologinmodel_intento_usuario_fecha_idx_and_more"),
    ]

    operations = [
        migrations.RunPython(crear_roles_base, migrations.RunPython.noop),
    ]
