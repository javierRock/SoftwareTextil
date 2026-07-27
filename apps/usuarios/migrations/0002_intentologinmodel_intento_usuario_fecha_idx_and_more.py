import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="intentologinmodel",
            index=models.Index(
                fields=["username", "fecha"],
                name="intento_usuario_fecha_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="sesionmodel",
            index=models.Index(
                fields=["usuario", "estado"],
                name="sesion_usuario_estado_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="sesionmodel",
            index=models.Index(
                fields=["fecha_expiracion"],
                name="sesion_expira_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="usuariomodel",
            index=models.Index(
                fields=["estado"],
                name="usuario_estado_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="rolmodel",
            constraint=models.UniqueConstraint(
                django.db.models.functions.text.Lower("nombre"),
                name="rol_nombre_unico_ci",
            ),
        ),
    ]
