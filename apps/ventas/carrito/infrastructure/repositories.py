"""Repositorios concretos con Django ORM para carrito de compras."""

from decimal import Decimal

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoCarrito
from apps.ventas.carrito.domain.carrito import CarritoCompras, ItemCarrito
from apps.ventas.carrito.domain.repositorios import RepositorioCarrito
from apps.ventas.carrito.infrastructure.models import CarritoModel, ItemCarritoModel


def _carrito_from_model(model: CarritoModel) -> CarritoCompras:
    carrito = CarritoCompras(
        id=str(model.id),
        cliente_id=model.cliente_id,
        estado=EstadoCarrito(model.estado),
    )
    for item_model in model.items.all():
        item = ItemCarrito(
            id=str(item_model.id),
            prenda_id=item_model.prenda_id,
            cantidad=item_model.cantidad,
            precio_unitario=Dinero(Decimal(item_model.precio_monto), item_model.precio_moneda),
        )
        carrito.items.append(item)
    return carrito


class DjangoRepositorioCarrito(RepositorioCarrito):
    def guardar(self, carrito: CarritoCompras) -> None:
        model = CarritoModel.objects.filter(id=carrito.id).first()
        if model is None:
            model = CarritoModel(id=carrito.id)
        model.cliente_id = carrito.cliente_id
        model.estado = carrito.estado.value
        model.save()

        model.items.all().delete()
        for item in carrito.items:
            ItemCarritoModel.objects.create(
                id=item.id,
                carrito=model,
                prenda_id=item.prenda_id,
                cantidad=item.cantidad,
                precio_monto=item.precio_unitario.monto,
                precio_moneda=item.precio_unitario.moneda,
            )

    def buscar_por_id(self, carrito_id: str) -> CarritoCompras | None:
        model = CarritoModel.objects.filter(id=carrito_id).first()
        return _carrito_from_model(model) if model else None

    def listar_por_cliente(self, cliente_id: str) -> list[CarritoCompras]:
        qs = CarritoModel.objects.filter(cliente_id=cliente_id)
        return [_carrito_from_model(m) for m in qs]
