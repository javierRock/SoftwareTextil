from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalogo", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipoproductomodel",
            name="activo",
            field=models.BooleanField(default=True),
        ),
    ]
