"""Repositorios concretos con Django ORM para carrito de compras.

`DjangoRepositorioCarrito` hereda el contrato completo `RepositorioCarrito` y
respeta su comportamiento esperado (LSP): no agrega precondiciones ni cambia el
tipo de retorno, por lo que puede sustituirse por cualquier otra
implementacion (ver `memoria.py`) sin tocar los servicios.
"""

from apps.compartido.domain.enums import EstadoCarrito
from apps.compartido.infrastructure.mapeo import a_dinero, de_dinero, uuid_valido
from apps.ventas.carrito.domain.carrito import CarritoCompras, ItemCarrito
from apps.ventas.carrito.domain.repositorios import RepositorioCarrito
from apps.ventas.carrito.infrastructure.models import CarritoModel, ItemCarritoModel


def _carrito_from_model(model: CarritoModel) -> CarritoCompras:
    carrito = CarritoCompras(
        id=str(model.id),
        cliente_id=str(model.cliente_id),
        estado=EstadoCarrito(model.estado),
        fecha_creacion=model.fecha_creacion,
    )
    for item_model in model.items.all():
        item = ItemCarrito(
            id=str(item_model.id),
            variante_id=str(item_model.variante_id),
            cantidad=item_model.cantidad,
            precio_unitario=a_dinero(
                item_model.precio_monto,
                item_model.precio_moneda,
            ),
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
            precio_monto, precio_moneda = de_dinero(item.precio_unitario)
            ItemCarritoModel.objects.create(
                id=item.id,
                carrito=model,
                variante_id=item.variante_id,
                cantidad=item.cantidad,
                precio_monto=precio_monto,
                precio_moneda=precio_moneda,
            )

    def buscar_por_id(self, carrito_id: str) -> CarritoCompras | None:
        if uuid_valido(carrito_id) is None:
            return None
        model = self._consulta().filter(id=carrito_id).first()
        return _carrito_from_model(model) if model else None

    def listar_por_cliente(self, cliente_id: str) -> list[CarritoCompras]:
        if uuid_valido(cliente_id) is None:
            return []
        qs = self._consulta().filter(cliente_id=cliente_id)
        return [_carrito_from_model(m) for m in qs]

    def listar_todos(self) -> list[CarritoCompras]:
        return [_carrito_from_model(m) for m in self._consulta()]

    @staticmethod
    def _consulta():
        """Trae el carrito y todos sus items sin una consulta por item."""
        return CarritoModel.objects.prefetch_related("items")
