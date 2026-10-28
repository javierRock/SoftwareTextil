"""Modelos ORM Django para catalogo."""

from typing import ClassVar

from django.db import models
from django.db.models.functions import Lower

from apps.compartido.domain.enums import EstadoPrenda, Moneda
from apps.compartido.infrastructure.campos import (
    campo_estado,
    campo_moneda,
    campo_monto,
    check_enum,
    check_monto_positivo,
    opciones,
)
from apps.compartido.infrastructure.models import ModeloBase


class CategoriaModel(ModeloBase):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(default="")
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "categorias"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(Lower("nombre"), name="categoria_nombre_unico_ci"),
        ]


class TipoProductoModel(ModeloBase):
    nombre = models.CharField(max_length=120)
    atributos_base = models.JSONField(default=dict)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = "tipos_producto"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(
                Lower("nombre"),
                name="tipo_producto_nombre_unico_ci",
            ),
        ]


class PrendaModel(ModeloBase):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(default="")
    precio_monto = campo_monto()
    precio_moneda = campo_moneda()
    imagen = models.ImageField(upload_to="catalogo/", null=True, blank=True)
    categoria = models.ForeignKey(
        CategoriaModel,
        on_delete=models.PROTECT,
        related_name="prendas",
    )
    tipo_producto = models.ForeignKey(
        TipoProductoModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prendas",
    )
    estado = campo_estado(EstadoPrenda, default=EstadoPrenda.ACTIVA)
    registrado_por = models.ForeignKey(
        "usuarios.UsuarioModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prendas_registradas",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "prendas"
        constraints: ClassVar[list[object]] = [
            check_enum("estado", EstadoPrenda, "prenda_estado_valido"),
            check_monto_positivo("precio", "prenda_precio_positivo"),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["categoria"], name="prenda_categoria_idx"),
            # El catalogo publico solo lista prendas activas.
            models.Index(
                fields=["nombre"],
                condition=models.Q(estado=EstadoPrenda.ACTIVA.value),
                name="prenda_activa_nombre_idx",
            ),
        ]


class VariantePrendaModel(ModeloBase):
    """Combinacion vendible de talla y color: la unidad que lleva stock."""

    prenda = models.ForeignKey(
        PrendaModel,
        on_delete=models.CASCADE,
        related_name="variantes",
    )
    sku = models.CharField(max_length=60, unique=True)
    talla = models.CharField(max_length=20)
    color = models.CharField(max_length=40, default="")
    # Sin precio propio, la variante hereda el de la prenda.
    precio_monto = campo_monto(null=True, blank=True)
    precio_moneda = models.CharField(
        max_length=3,
        choices=opciones(Moneda),
        null=True,
        blank=True,
        default=None,
    )
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "variantes_prenda"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(
                fields=["prenda", "talla", "color"],
                name="variante_combinacion_unica",
            ),
            # El precio es opcional, pero si existe debe estar completo y ser
            # positivo: nunca un monto sin moneda ni una moneda sin monto.
            models.CheckConstraint(
                condition=(
                    models.Q(precio_monto__isnull=True, precio_moneda__isnull=True)
                    | models.Q(precio_monto__gt=0, precio_moneda__isnull=False)
                ),
                name="variante_precio_completo",
            ),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["prenda"], name="variante_prenda_idx"),
        ]
