"""Adaptador de persistencia de pagos basado en Django ORM."""

from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPago, MetodoPago
from apps.ventas.pagos.domain.pago import Pago
from apps.ventas.pagos.domain.repositorios import RepositorioPago
from apps.ventas.pagos.infrastructure.models import PagoModel


def pago_desde_modelo(modelo: PagoModel) -> Pago:
    """Convierte un registro ORM en un agregado de dominio."""

    return Pago(
        id=str(modelo.id),
        pedido_id=modelo.pedido_id,
        monto=Dinero(modelo.monto_monto, modelo.monto_moneda),
        metodo=MetodoPago(modelo.metodo),
        referencia=modelo.referencia,
        estado=EstadoPago(modelo.estado),
        fecha=modelo.fecha,
    )


class DjangoRepositorioPago(RepositorioPago):
    """Implementa el contrato de pagos encapsulando Django ORM."""

    def guardar(self, pago: Pago) -> None:
        modelo, creado = PagoModel.objects.update_or_create(
            id=pago.id,
            defaults={
                "pedido_id": pago.pedido_id,
                "monto_monto": pago.monto.monto,
                "monto_moneda": pago.monto.moneda,
                "metodo": pago.metodo.value,
                "referencia": pago.referencia,
                "estado": pago.estado.value,
            },
        )
        if creado:
            pago.fecha = modelo.fecha

    def buscar_por_id(self, pago_id: str) -> Pago | None:
        modelo = PagoModel.objects.filter(id=pago_id).first()
        return pago_desde_modelo(modelo) if modelo is not None else None

    def listar(self) -> list[Pago]:
        modelos = PagoModel.objects.order_by("fecha", "id")
        return [pago_desde_modelo(modelo) for modelo in modelos]

    def listar_por_pedido(self, pedido_id: str) -> list[Pago]:
        modelos = PagoModel.objects.filter(pedido_id=pedido_id).order_by(
            "fecha",
            "id",
        )
        return [pago_desde_modelo(modelo) for modelo in modelos]
