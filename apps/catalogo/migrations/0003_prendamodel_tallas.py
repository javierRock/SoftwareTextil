from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0002_tipoproductomodel_activo"),
    ]

    operations = [
        migrations.AddField(
            model_name="prendamodel",
            name="tallas",
            field=models.JSONField(default=list),
        ),
    ]
