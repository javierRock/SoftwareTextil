"""Modelos ORM de carrito, pedidos y pagos de la app ventas."""

import uuid
from typing import ClassVar

from django.db import models

from apps.compartido.domain.enums import EstadoPago, MetodoPago


class CarritoModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    cliente_id = models.CharField(max_length=36)
    estado = models.CharField(max_length=30, default="abierto")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "carritos"


class ItemCarritoModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    carrito = models.ForeignKey(
        CarritoModel, on_delete=models.CASCADE, related_name="items"
    )
    prenda_id = models.CharField(max_length=36)
    cantidad = models.IntegerField()
    precio_monto = models.DecimalField(max_digits=12, decimal_places=2)
    precio_moneda = models.CharField(max_length=3, default="PEN")

    class Meta:
        db_table = "items_carrito"


class PedidoModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    cliente_id = models.CharField(max_length=36)
    carrito_id = models.CharField(max_length=36)
    total_monto = models.DecimalField(max_digits=12, decimal_places=2)
    total_moneda = models.CharField(max_length=3, default="PEN")
    estado = models.CharField(max_length=30, default="creado")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pedidos"


class DetallePedidoModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    pedido = models.ForeignKey(
        PedidoModel, on_delete=models.CASCADE, related_name="detalles"
    )
    prenda_id = models.CharField(max_length=36)
    cantidad = models.IntegerField()
    precio_monto = models.DecimalField(max_digits=12, decimal_places=2)
    precio_moneda = models.CharField(max_length=3, default="PEN")

    class Meta:
        db_table = "detalles_pedido"


class PagoModel(models.Model):
    id = models.CharField(max_length=36, primary_key=True, default=uuid.uuid4)
    pedido_id = models.CharField(max_length=36)
    monto_monto = models.DecimalField(max_digits=12, decimal_places=2)
    monto_moneda = models.CharField(max_length=3, default="PEN")
    metodo = models.CharField(max_length=30)
    referencia = models.CharField(max_length=120, default="")
    estado = models.CharField(max_length=30, default="pendiente")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pagos"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(
                fields=["pedido_id"],
                name="pago_pedido_unico",
            ),
            models.CheckConstraint(
                condition=models.Q(monto_monto__gt=0),
                name="pago_monto_positivo",
            ),
            models.CheckConstraint(
                condition=models.Q(estado__in=[estado.value for estado in EstadoPago]),
                name="pago_estado_valido",
            ),
            models.CheckConstraint(
                condition=models.Q(metodo__in=[metodo.value for metodo in MetodoPago]),
                name="pago_metodo_valido",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(metodo=MetodoPago.EFECTIVO.value)
                    | ~models.Q(referencia="")
                ),
                name="pago_referencia_requerida",
            ),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["fecha", "id"], name="pago_fecha_id_idx"),
        ]
