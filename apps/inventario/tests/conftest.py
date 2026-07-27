"""Fixtures compartidas para las pruebas de inventario.

Se apoyan en las fabricas del `conftest.py` de la raiz (`crear_categoria`,
`crear_prenda`, `crear_variante`, `crear_usuario`), porque el esquema tiene
claves foraneas reales: una prueba ya no puede inventar identificadores.
"""

import pytest
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import VariantePrendaModel
from apps.catalogo.infrastructure.repositories import (
    DjangoRepositorioCatalogo,
    DjangoRepositorioVariante,
)
from apps.inventario.application.services import ServicioInventario
from apps.inventario.infrastructure.models import StockVarianteModel
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioAlertaStock,
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)
from apps.usuarios.presentation.authentication import UsuarioAutenticado

CANTIDAD_INICIAL = 10
NIVEL_MINIMO = 3


@pytest.fixture
def categoria(crear_categoria):
    return crear_categoria(nombre="Camisetas")


@pytest.fixture
def prenda(crear_prenda, categoria):
    prenda = crear_prenda()
    prenda.categoria = categoria
    prenda.save()
    return prenda


@pytest.fixture
def variante(crear_variante, prenda) -> VariantePrendaModel:
    return crear_variante(prenda=prenda, talla="M")


@pytest.fixture
def variante_id(variante: VariantePrendaModel) -> str:
    return str(variante.id)


@pytest.fixture
def stock(variante: VariantePrendaModel) -> StockVarianteModel:
    return StockVarianteModel.objects.create(
        variante=variante,
        cantidad_actual=CANTIDAD_INICIAL,
        nivel_minimo=NIVEL_MINIMO,
        ubicacion="almacen",
        unidad="unidad",
    )


@pytest.fixture
def servicio_inventario() -> ServicioInventario:
    return ServicioInventario(
        DjangoRepositorioInventario(),
        DjangoRepositorioMovimiento(),
        DjangoRepositorioAlertaStock(),
        DjangoRepositorioVariante(),
        DjangoRepositorioCatalogo(),
    )


@pytest.fixture
def usuario_autenticado(crear_usuario) -> UsuarioAutenticado:
    """El proyecto no usa el modelo `auth.User`, sino su propia sesion."""
    usuario = crear_usuario(nombre="Encargado", rol="Encargado de inventario")
    return UsuarioAutenticado(
        id=str(usuario.id),
        nombre=usuario.nombre,
        username=usuario.username,
        email=usuario.email,
        rol=usuario.rol.nombre,
    )


@pytest.fixture
def usuario_id(usuario_autenticado: UsuarioAutenticado) -> str:
    return usuario_autenticado.id


@pytest.fixture
def client(usuario_autenticado: UsuarioAutenticado) -> APIClient:
    api_client = APIClient()
    api_client.force_authenticate(user=usuario_autenticado)
    return api_client
