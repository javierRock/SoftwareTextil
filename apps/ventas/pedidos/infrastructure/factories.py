"""Composition root del modulo de pedidos.

Unico lugar del modulo que conoce implementaciones concretas de persistencia
(DIP): la capa de presentacion pide un caso de uso ya armado y nunca importa el
ORM. Cambiar de adaptador (Django, memoria, otro motor) se resuelve aqui.
"""

from apps.ventas.carrito.infrastructure.repositories import DjangoRepositorioCarrito
from apps.ventas.pedidos.application.consultas import ConsultaPedidos
from apps.ventas.pedidos.application.services import ServicioPedidos
from apps.ventas.pedidos.infrastructure.repositories import DjangoRepositorioPedido


def construir_servicio_pedidos() -> ServicioPedidos:
    repositorio_pedido = DjangoRepositorioPedido()
    repositorio_carrito = DjangoRepositorioCarrito()
    return ServicioPedidos(
        lector_pedido=repositorio_pedido,
        escritor_pedido=repositorio_pedido,
        lector_carrito=repositorio_carrito,
        escritor_carrito=repositorio_carrito,
    )


def construir_consulta_pedidos() -> ConsultaPedidos:
    repositorio = DjangoRepositorioPedido()
    return ConsultaPedidos(lector=repositorio, catalogo=repositorio)
