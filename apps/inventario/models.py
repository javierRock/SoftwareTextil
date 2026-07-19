"""Modelos ORM Django para inventario."""

import uuid

from django.db import models


class StockPrendaModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    prenda_id = models.CharField(max_length=36)
    cantidad_actual = models.IntegerField()
    nivel_minimo = models.IntegerField()
    ubicacion = models.CharField(max_length=120, default="almacen")
    unidad = models.CharField(max_length=30, default="unidad")
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stocks_prenda"
        unique_together = [("prenda_id",)]


class MovimientoInventarioModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    stock = models.ForeignKey(StockPrendaModel, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=30)
    cantidad = models.IntegerField()
    motivo = models.TextField()
    registrado_por = models.CharField(max_length=36)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "movimientos_inventario"


class AlertaStockModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    stock = models.ForeignKey(StockPrendaModel, on_delete=models.CASCADE, related_name="alertas")
    nivel_actual = models.IntegerField()
    nivel_minimo = models.IntegerField()
    estado = models.CharField(max_length=30, default="pendiente")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alertas_stock"
