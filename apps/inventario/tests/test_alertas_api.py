"""Pruebas de API para alertas de stock bajo."""

import pytest

from apps.catalogo.infrastructure.models import CategoriaModel, PrendaModel
from apps.inventario.infrastructure.models import StockPrendaModel


@pytest.mark.django_db
def test_bajo_minimo_devuelve_prendas_que_cruzaron_el_umbral(client, stock, prenda, django_assert_num_queries) -> None:
    categoria = CategoriaModel.objects.create(id="categoria-2", nombre="Jeans", descripcion="Categoria secundaria")
    PrendaModel.objects.create(
        id="prenda-2",
        nombre="Jean de prueba",
        descripcion="Jean en stock exacto",
        precio_monto="40.00",
        precio_moneda="PEN",
        categoria=categoria,
        estado="activa",
        registrado_por="usuario-1",
    )
    StockPrendaModel.objects.create(
        id="stock-2",
        prenda_id="prenda-2",
        cantidad_actual=3,
        nivel_minimo=3,
        ubicacion="almacen",
        unidad="unidad",
    )

    client.post(
        "/api/stock/salidas/",
        {"prenda_id": prenda.id, "cantidad": 8, "motivo": "Salida", "usuario_id": "usuario-1"},
        format="json",
    )

    with django_assert_num_queries(2):
        respuesta = client.get("/api/stock/bajo-minimo/")

    assert respuesta.status_code == 200
    assert respuesta.data == [
        {
            "categoria_id": "categoria-1",
            "categoria": "Camisetas",
            "prenda_id": "prenda-1",
            "prenda": "Polo",
            "cantidad_actual": 2,
            "nivel_minimo": 3,
        }
    ]


@pytest.mark.django_db
def test_bajo_minimo_incluye_stock_cero(client, categoria) -> None:
    PrendaModel.objects.create(
        id="prenda-cero",
        nombre="Polo cero",
        descripcion="Sin stock",
        precio_monto="25.00",
        precio_moneda="PEN",
        categoria=categoria,
        estado="activa",
        registrado_por="usuario-1",
    )
    StockPrendaModel.objects.create(
        id="stock-cero",
        prenda_id="prenda-cero",
        cantidad_actual=0,
        nivel_minimo=1,
        ubicacion="almacen",
        unidad="unidad",
    )

    respuesta = client.get("/api/stock/bajo-minimo/")

    assert respuesta.status_code == 200
    assert respuesta.data == [
        {
            "categoria_id": "categoria-1",
            "categoria": "Camisetas",
            "prenda_id": "prenda-cero",
            "prenda": "Polo cero",
            "cantidad_actual": 0,
            "nivel_minimo": 1,
        }
    ]


@pytest.mark.django_db
def test_bajo_minimo_devuelve_lista_vacia_si_no_hay_alertas(client, stock, prenda) -> None:
    respuesta = client.get("/api/stock/bajo-minimo/")

    assert respuesta.status_code == 200
    assert respuesta.data == []


@pytest.mark.django_db
def test_bajo_minimo_rechaza_solicitudes_sin_autenticacion() -> None:
    from rest_framework.test import APIClient

    respuesta = APIClient().get("/api/stock/bajo-minimo/")

    assert respuesta.status_code in {401, 403}
