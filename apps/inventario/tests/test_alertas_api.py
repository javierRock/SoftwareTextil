"""Pruebas de API para alertas de stock bajo.

La reposicion se decide por variante: lo que falta es la talla M, no la camisa
entera. Por eso la alerta identifica el SKU concreto que hay que pedir.
"""

import pytest
from rest_framework.test import APIClient

from apps.inventario.infrastructure.models import StockVarianteModel

pytestmark = pytest.mark.django_db

URL = "/api/stock/bajo-minimo/"


def test_bajo_minimo_devuelve_las_variantes_que_cruzaron_el_umbral(
    client,
    stock,
    variante,
    variante_id,
    crear_variante,
) -> None:
    """Una variante justo en el minimo no alerta; por debajo, si."""
    en_el_limite = crear_variante(prenda=variante.prenda, talla="S")
    StockVarianteModel.objects.create(
        variante=en_el_limite,
        cantidad_actual=3,
        nivel_minimo=3,
    )

    client.post(
        "/api/stock/salidas/",
        {"variante_id": variante_id, "cantidad": 8, "motivo": "Salida"},
        format="json",
    )

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert len(respuesta.data) == 1
    alerta = respuesta.data[0]
    assert alerta["categoria"] == "Camisetas"
    assert alerta["variante_id"] == variante_id
    assert alerta["sku"] == variante.sku
    assert alerta["talla"] == "M"
    assert alerta["cantidad_actual"] == 2
    assert alerta["nivel_minimo"] == 3
    assert alerta["faltante"] == 1


def test_bajo_minimo_incluye_las_variantes_en_cero(client, crear_variante) -> None:
    agotada = crear_variante(talla="L")
    StockVarianteModel.objects.create(
        variante=agotada,
        cantidad_actual=0,
        nivel_minimo=2,
    )

    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert len(respuesta.data) == 1
    assert respuesta.data[0]["cantidad_actual"] == 0
    assert respuesta.data[0]["faltante"] == 2


def test_bajo_minimo_devuelve_lista_vacia_si_no_hay_alertas(client, stock) -> None:
    respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert respuesta.data == []


def test_bajo_minimo_rechaza_solicitudes_sin_autenticacion() -> None:
    respuesta = APIClient().get(URL)

    assert respuesta.status_code in {401, 403}


def test_bajo_minimo_no_sufre_problema_n_mas_uno(
    client,
    crear_variante,
    django_assert_num_queries,
) -> None:
    """Las claves foraneas resuelven categoria y prenda en la misma consulta."""
    for talla in ("XS", "S", "M", "L"):
        StockVarianteModel.objects.create(
            variante=crear_variante(talla=talla),
            cantidad_actual=0,
            nivel_minimo=5,
        )

    with django_assert_num_queries(1):
        respuesta = client.get(URL)

    assert respuesta.status_code == 200
    assert len(respuesta.data) == 4
