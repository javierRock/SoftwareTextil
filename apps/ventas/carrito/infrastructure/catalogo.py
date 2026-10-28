"""Consulta de precio y disponibilidad usada por el carrito HTTP."""

from apps.catalogo.models import VariantePrendaModel
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda
from apps.compartido.infrastructure.mapeo import uuid_valido
from apps.inventario.models import StockVarianteModel
from apps.ventas.carrito.domain.errors import (
    StockInsuficienteError,
    VarianteNoDisponibleError,
)


def obtener_precio_disponible(variante_id: str, cantidad: int) -> Dinero:
    if uuid_valido(variante_id) is None:
        raise VarianteNoDisponibleError
    variante = (
        VariantePrendaModel.objects.select_related("prenda")
        .filter(id=variante_id)
        .first()
    )
    if (
        variante is None
        or not variante.activa
        or variante.prenda.estado != EstadoPrenda.ACTIVA.value
    ):
        raise VarianteNoDisponibleError

    stock = StockVarianteModel.objects.filter(variante_id=variante_id).first()
    if stock is None or stock.cantidad_actual - stock.cantidad_reservada < cantidad:
        raise StockInsuficienteError

    monto = variante.precio_monto
    moneda = variante.precio_moneda
    if monto is None or not moneda:
        monto = variante.prenda.precio_monto
        moneda = variante.prenda.precio_moneda
    return Dinero(monto, moneda)
