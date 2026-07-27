"""Modelos abstractos que fijan la identidad y la auditoria de las tablas.

Toda tabla del sistema hereda de `ModeloBase`, de modo que la decision sobre el
tipo de clave primaria se toma una sola vez. La identidad se genera en el
dominio (las fabricas devuelven `str(uuid4())`); el `default` de aqui solo
cubre las filas creadas directamente por el ORM, como las de las migraciones de
datos.
"""

from uuid import uuid4

from django.db import models


class ModeloBase(models.Model):
    """Identidad comun: UUID nativo como clave primaria."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class ModeloAuditado(ModeloBase):
    """Identidad mas las marcas de tiempo del objeto de valor `DatosAuditoria`."""

    creado_en = models.DateTimeField(auto_now_add=True)
    modificado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
