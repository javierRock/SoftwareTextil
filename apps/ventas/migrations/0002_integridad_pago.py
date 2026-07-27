"""Restricciones de integridad para el agregado Pago."""

from typing import ClassVar

from django.db import migrations, models
from django.db.models import Count

METODOS = ("efectivo", "tarjeta", "transferencia", "yape")
ESTADOS = ("pendiente", "aprobado", "rechazado")


def validar_pagos_existentes(apps, schema_editor):
    pago_model = apps.get_model("ventas", "PagoModel")
    invalidos = pago_model.objects.filter(monto_monto__lte=0).count()
    invalidos += pago_model.objects.exclude(metodo__in=METODOS).count()
    invalidos += pago_model.objects.exclude(estado__in=ESTADOS).count()
    invalidos += (
        pago_model.objects.exclude(metodo="efectivo").filter(referencia="").count()
    )
    duplicados = (
        pago_model.objects.values("pedido_id")
        .annotate(total=Count("id"))
        .filter(total__gt=1)
        .count()
    )
    if invalidos or duplicados:
        raise RuntimeError(
            "No se pueden aplicar las restricciones de pagos: "
            f"{invalidos} registros invalidos y {duplicados} pedidos duplicados."
        )


class Migration(migrations.Migration):
    dependencies: ClassVar[list[tuple[str, str]]] = [("ventas", "0001_initial")]

    operations: ClassVar[list[object]] = [
        migrations.RunPython(validar_pagos_existentes, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="pagomodel",
            constraint=models.UniqueConstraint(
                fields=("pedido_id",),
                name="pago_pedido_unico",
            ),
        ),
        migrations.AddConstraint(
            model_name="pagomodel",
            constraint=models.CheckConstraint(
                condition=models.Q(("monto_monto__gt", 0)),
                name="pago_monto_positivo",
            ),
        ),
        migrations.AddConstraint(
            model_name="pagomodel",
            constraint=models.CheckConstraint(
                condition=models.Q(("estado__in", ESTADOS)),
                name="pago_estado_valido",
            ),
        ),
        migrations.AddConstraint(
            model_name="pagomodel",
            constraint=models.CheckConstraint(
                condition=models.Q(("metodo__in", METODOS)),
                name="pago_metodo_valido",
            ),
        ),
        migrations.AddConstraint(
            model_name="pagomodel",
            constraint=models.CheckConstraint(
                condition=models.Q(("metodo", "efectivo"))
                | ~models.Q(("referencia", "")),
                name="pago_referencia_requerida",
            ),
        ),
        migrations.AddIndex(
            model_name="pagomodel",
            index=models.Index(
                fields=["fecha", "id"],
                name="pago_fecha_id_idx",
            ),
        ),
    ]
