"""Modelos ORM Django para catalogo."""

import uuid

from django.db import models


class CategoriaModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(default="")

    class Meta:
        db_table = "categorias"


class TipoProductoModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=120)
    atributos_base = models.JSONField(default=dict)

    class Meta:
        db_table = "tipos_producto"


class PrendaModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(default="")
    precio_monto = models.DecimalField(max_digits=12, decimal_places=2)
    precio_moneda = models.CharField(max_length=3, default="PEN")
    categoria = models.ForeignKey(CategoriaModel, on_delete=models.PROTECT)
    tipo_producto = models.ForeignKey(TipoProductoModel, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=30, default="activa")
    registrado_por = models.CharField(max_length=36, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "prendas"
