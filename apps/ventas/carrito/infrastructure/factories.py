"""Composition root del modulo de carrito de compras.

Unico lugar del modulo que conoce implementaciones concretas de persistencia
(DIP): la capa de presentacion pide un caso de uso ya armado y nunca importa el
ORM. Cambiar de adaptador (Django, memoria, otro motor) se resuelve aqui.
"""

from apps.ventas.carrito.application.consultas import ConsultaCarritos
from apps.ventas.carrito.application.services import ServicioCompras
from apps.ventas.carrito.infrastructure.repositories import DjangoRepositorioCarrito


def construir_servicio_compras() -> ServicioCompras:
    repositorio = DjangoRepositorioCarrito()
    return ServicioCompras(lector=repositorio, escritor=repositorio)


def construir_consulta_carritos() -> ConsultaCarritos:
    repositorio = DjangoRepositorioCarrito()
    return ConsultaCarritos(lector=repositorio, catalogo=repositorio)
