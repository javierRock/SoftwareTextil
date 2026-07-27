"""Fixtures compartidas para las pruebas de inventario."""

from decimal import Decimal

from django.contrib.auth import get_user_model
import pytest
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel
from apps.catalogo.infrastructure.repositories import DjangoRepositorioCatalogo, DjangoRepositorioPrenda
from apps.inventario.application.services import ServicioInventario
from apps.inventario.infrastructure.models import StockPrendaModel
from apps.inventario.infrastructure.repositories import (
    DjangoRepositorioAlertaStock,
    DjangoRepositorioInventario,
    DjangoRepositorioMovimiento,
)


@pytest.fixture
def categoria() -> CategoriaModel:
    return CategoriaModel.objects.create(id="categoria-1", nombre="Camisetas", descripcion="Categoria base")


@pytest.fixture
def prenda(categoria: CategoriaModel) -> PrendaModel:
    return PrendaModel.objects.create(
        id="prenda-1",
        nombre="Polo",
        descripcion="Polo de prueba",
        precio_monto=Decimal("25.00"),
        precio_moneda="PEN",
        categoria=categoria,
        estado="activa",
        registrado_por="usuario-1",
    )


@pytest.fixture
def stock(prenda: PrendaModel) -> StockPrendaModel:
    return StockPrendaModel.objects.create(
        id="stock-1",
        prenda_id=prenda.id,
        cantidad_actual=10,
        nivel_minimo=3,
        ubicacion="almacen",
        unidad="unidad",
    )


@pytest.fixture
def servicio_inventario() -> ServicioInventario:
    return ServicioInventario(
        DjangoRepositorioInventario(),
        DjangoRepositorioMovimiento(),
        DjangoRepositorioAlertaStock(),
        DjangoRepositorioPrenda(),
        DjangoRepositorioCatalogo(),
    )


@pytest.fixture
def usuario_autenticado():
    return get_user_model().objects.create_user(username="inventario-test", password="test-pass-123")


@pytest.fixture
def client(usuario_autenticado):
    api_client = APIClient()
    api_client.force_authenticate(user=usuario_autenticado)
    return api_client
