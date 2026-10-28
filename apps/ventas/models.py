"""Modelos ORM de carrito, pedidos, pagos y despachos de la app ventas."""

from typing import ClassVar

from django.db import models

from apps.compartido.domain.enums import (
    EstadoCarrito,
    EstadoDespacho,
    EstadoPago,
    EstadoPedido,
    MetodoPago,
)
from apps.compartido.infrastructure.campos import (
    campo_estado,
    campo_moneda,
    campo_monto,
    check_enum,
    check_monto_positivo,
    check_positivo,
)
from apps.compartido.infrastructure.models import ModeloBase


class CarritoModel(ModeloBase):
    cliente = models.ForeignKey(
        "usuarios.UsuarioModel",
        on_delete=models.PROTECT,
        related_name="carritos",
    )
    estado = campo_estado(EstadoCarrito, default=EstadoCarrito.ABIERTO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "carritos"
        constraints: ClassVar[list[object]] = [
            check_enum("estado", EstadoCarrito, "carrito_estado_valido"),
            # Unicidad parcial: un cliente solo puede tener un carrito abierto.
            # Los carritos convertidos o cancelados quedan como historico.
            models.UniqueConstraint(
                fields=["cliente"],
                condition=models.Q(estado=EstadoCarrito.ABIERTO.value),
                name="carrito_abierto_unico_por_cliente",
            ),
        ]


class ItemCarritoModel(ModeloBase):
    carrito = models.ForeignKey(
        CarritoModel,
        on_delete=models.CASCADE,
        related_name="items",
    )
    variante = models.ForeignKey(
        "catalogo.VariantePrendaModel",
        on_delete=models.PROTECT,
        related_name="items_carrito",
    )
    cantidad = models.IntegerField()
    precio_monto = campo_monto()
    precio_moneda = campo_moneda()

    class Meta:
        db_table = "items_carrito"
        constraints: ClassVar[list[object]] = [
            check_positivo("cantidad", "item_carrito_cantidad_positiva"),
            check_monto_positivo("precio", "item_carrito_precio_positivo"),
            # El agregado fusiona el item cuando se repite la variante, asi que
            # la tabla nunca debe contener dos lineas de la misma variante.
            models.UniqueConstraint(
                fields=["carrito", "variante"],
                name="item_carrito_variante_unica",
            ),
        ]


class PedidoModel(ModeloBase):
    cliente = models.ForeignKey(
        "usuarios.UsuarioModel",
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    carrito = models.OneToOneField(
        CarritoModel,
        on_delete=models.PROTECT,
        related_name="pedido",
    )
    total_monto = campo_monto()
    total_moneda = campo_moneda()
    estado = campo_estado(EstadoPedido, default=EstadoPedido.CREADO)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pedidos"
        constraints: ClassVar[list[object]] = [
            check_enum("estado", EstadoPedido, "pedido_estado_valido"),
            check_monto_positivo("total", "pedido_total_positivo"),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(
                fields=["cliente", "-fecha_creacion"],
                name="pedido_cliente_fecha_idx",
            ),
            models.Index(fields=["estado"], name="pedido_estado_idx"),
        ]


class DetallePedidoModel(ModeloBase):
    pedido = models.ForeignKey(
        PedidoModel,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    variante = models.ForeignKey(
        "catalogo.VariantePrendaModel",
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    cantidad = models.IntegerField()
    precio_monto = campo_monto()
    precio_moneda = campo_moneda()

    class Meta:
        db_table = "detalles_pedido"
        constraints: ClassVar[list[object]] = [
            check_positivo("cantidad", "detalle_pedido_cantidad_positiva"),
            check_monto_positivo("precio", "detalle_pedido_precio_positivo"),
            models.UniqueConstraint(
                fields=["pedido", "variante"],
                name="detalle_pedido_variante_unica",
            ),
        ]


class PagoModel(ModeloBase):
    pedido = models.OneToOneField(
        PedidoModel,
        on_delete=models.CASCADE,
        related_name="pago",
    )
    monto_monto = campo_monto()
    monto_moneda = campo_moneda()
    metodo = campo_estado(MetodoPago, default=MetodoPago.EFECTIVO)
    referencia = models.CharField(max_length=120, default="")
    estado = campo_estado(EstadoPago, default=EstadoPago.PENDIENTE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pagos"
        constraints: ClassVar[list[object]] = [
            # `OneToOneField` ya impone un pago por pedido; se conserva el
            # nombre historico de la restriccion para no perder su trazabilidad.
            models.UniqueConstraint(
                fields=["pedido"],
                name="pago_pedido_unico",
            ),
            check_monto_positivo("monto", "pago_monto_positivo"),
            check_enum("estado", EstadoPago, "pago_estado_valido"),
            check_enum("metodo", MetodoPago, "pago_metodo_valido"),
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


class DespachoModel(ModeloBase):
    """Preparacion y entrega fisica de un pedido."""

    pedido = models.OneToOneField(
        PedidoModel,
        on_delete=models.PROTECT,
        related_name="despacho",
    )
    direccion_entrega = models.CharField(max_length=250)
    estado = campo_estado(EstadoDespacho, default=EstadoDespacho.PENDIENTE)
    responsable = models.ForeignKey(
        "usuarios.UsuarioModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="despachos_atendidos",
    )
    fecha_preparacion = models.DateTimeField(null=True, blank=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "despachos"
        constraints: ClassVar[list[object]] = [
            check_enum("estado", EstadoDespacho, "despacho_estado_valido"),
            # Un despacho confirmado siempre deja constancia de cuando lo fue.
            models.CheckConstraint(
                condition=(
                    ~models.Q(estado=EstadoDespacho.CONFIRMADO.value)
                    | models.Q(fecha_confirmacion__isnull=False)
                ),
                name="despacho_confirmado_con_fecha",
            ),
        ]
        indexes: ClassVar[list[object]] = [
            models.Index(fields=["estado"], name="despacho_estado_idx"),
        ]


class GuiaRemisionModel(ModeloBase):
    """Documento que acompana el traslado; uno por despacho confirmado."""

    despacho = models.OneToOneField(
        DespachoModel,
        on_delete=models.CASCADE,
        related_name="guia",
    )
    serie = models.CharField(max_length=10)
    numero = models.CharField(max_length=20)
    transportista = models.CharField(max_length=120, default="")
    fecha_emision = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "guias_remision"
        constraints: ClassVar[list[object]] = [
            models.UniqueConstraint(
                fields=["serie", "numero"],
                name="guia_serie_numero_unica",
            ),
        ]
