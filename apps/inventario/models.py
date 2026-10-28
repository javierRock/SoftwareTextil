"""Modelos ORM Django para inventario."""

from typing import ClassVar

from django.db import models

from apps.compartido.domain.enums import EstadoAlerta, TipoMovimiento
from apps.compartido.infrastructure.campos import (
    campo_estado,
    check_enum,
    check_no_negativo,
    check_positivo,
)
from apps.compartido.infrastructure.models import ModeloBase


class StockVarianteModel(ModeloBase):
    """Existencias de una variante: relacion uno a uno con `variantes_prenda`."""

    variante = models.OneToOneField(
        "catalogo.VariantePrendaModel",
        on_delete=models.PROTECT,
        related_name="stock",
    )
    cantidad_actual = models.IntegerField(default=0)
    cantidad_reservada = models.IntegerField(default=0)
    nivel_minimo = models.IntegerField(default=0)
    ubicacion = models.CharField(max_length=120, default="almacen")
    unidad = models.CharField(max_length=30, default="unidad")
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stocks_variante"
        constraints: ClassVar[list[object]] = [
            # Respaldo en base de datos del invariante del objeto de valor
            # `Stock`: una existencia nunca puede quedar en negativo.
            check_no_negativo("cantidad_actual", "stock_cantidad_no_negativa"),
            check_no_negativo("cantidad_reservada", "stock_reservada_no_negativa"),
            check_no_negativo("nivel_minimo", "stock_nivel_minimo_no_negativo"),
            models.CheckConstraint(
                condition=models.Q(
                    cantidad_reservada__lte=models.F("cantidad_actual")
                ),
                name="stock_reservada_no_excede_actual",
            ),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["ubicacion"], name="stock_ubicacion_idx"),
        ]


class MovimientoInventarioModel(ModeloBase):
    """Historico inmutable: una vez registrado, un movimiento no se modifica."""

    stock = models.ForeignKey(
        StockVarianteModel,
        on_delete=models.PROTECT,
        related_name="movimientos",
    )
    tipo = campo_estado(TipoMovimiento, default=TipoMovimiento.INGRESO)
    cantidad = models.IntegerField()
    motivo = models.TextField()
    registrado_por = models.ForeignKey(
        "usuarios.UsuarioModel",
        on_delete=models.PROTECT,
        related_name="movimientos_registrados",
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "movimientos_inventario"
        constraints: ClassVar[list[object]] = [
            check_enum("tipo", TipoMovimiento, "movimiento_tipo_valido"),
            check_positivo("cantidad", "movimiento_cantidad_positiva"),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["stock", "-fecha"], name="movimiento_stock_fecha_idx"),
        ]


class AlertaStockModel(ModeloBase):
    stock = models.ForeignKey(
        StockVarianteModel,
        on_delete=models.CASCADE,
        related_name="alertas",
    )
    nivel_actual = models.IntegerField()
    nivel_minimo = models.IntegerField()
    estado = campo_estado(EstadoAlerta, default=EstadoAlerta.PENDIENTE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alertas_stock"
        constraints: ClassVar[list[object]] = [
            check_enum("estado", EstadoAlerta, "alerta_estado_valido"),
            # Unicidad parcial: un stock no puede acumular dos alertas
            # pendientes a la vez. Antes esto solo lo cuidaba el servicio.
            models.UniqueConstraint(
                fields=["stock"],
                condition=models.Q(estado=EstadoAlerta.PENDIENTE.value),
                name="alerta_pendiente_unica_por_stock",
            ),
        ]
