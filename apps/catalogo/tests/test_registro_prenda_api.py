import pytest

from apps.catalogo.infrastructure.models import (
    CategoriaModel,
    PrendaModel,
    TipoProductoModel,
)
from apps.inventario.models import (
    AlertaStockModel,
    MovimientoInventarioModel,
    StockVarianteModel,
)

pytestmark = pytest.mark.django_db


def test_api_registra_solo_la_ficha_comercial_de_la_prenda(cliente_admin) -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    tipo = TipoProductoModel.objects.create(nombre="Camisa")
    cliente, usuario = cliente_admin

    respuesta = cliente.post(
        "/api/prendas/",
        {
            "nombre": "Camisa clasica",
            "descripcion": "Algodon",
            "precio_monto": "49.90",
            "precio_moneda": "PEN",
            "categoria_id": str(categoria.id),
            "tipo_producto_id": str(tipo.id),
            "tallas": ["M", "L", "40", "41"],
            "registrado_por": str(usuario.id),
        },
        format="json",
    )

    assert respuesta.status_code == 201
    assert respuesta.data["nombre"] == "Camisa clasica"
    assert respuesta.data["precio_monto"] == "49.90"
    assert respuesta.data["precio_moneda"] == "PEN"
    assert respuesta.data["categoria_id"] == str(categoria.id)
    assert respuesta.data["tipo_producto_id"] == str(tipo.id)
    assert respuesta.data["tallas"] == ["M", "L", "40", "41"]
    assert respuesta.data["registrado_por"] == str(usuario.id)
    assert PrendaModel.objects.filter(id=respuesta.data["id"]).exists()
    assert StockVarianteModel.objects.count() == 0
    assert MovimientoInventarioModel.objects.count() == 0
    assert AlertaStockModel.objects.count() == 0


@pytest.mark.parametrize(
    "cambio",
    [
        {"nombre": ""},
        {"precio_monto": "0"},
        {"precio_monto": "-1"},
        {"precio_moneda": "SOLES"},
    ],
)
def test_api_rechaza_datos_comerciales_invalidos(cambio, cliente_admin) -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    datos = {
        "nombre": "Camisa",
        "precio_monto": "10.00",
        "precio_moneda": "PEN",
        "categoria_id": str(categoria.id),
    }
    datos.update(cambio)

    cliente, _ = cliente_admin
    respuesta = cliente.post("/api/prendas/", datos, format="json")

    assert respuesta.status_code == 400
    assert PrendaModel.objects.count() == 0


def test_api_impide_registro_con_categoria_inexistente(cliente_admin) -> None:
    cliente, _ = cliente_admin
    respuesta = cliente.post(
        "/api/prendas/",
        {
            "nombre": "Camisa",
            "precio_monto": "10.00",
            "categoria_id": "categoria-inexistente",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert "error" in respuesta.data
    assert PrendaModel.objects.count() == 0


def test_api_impide_registro_con_tipo_inexistente(cliente_admin) -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    cliente, _ = cliente_admin

    respuesta = cliente.post(
        "/api/prendas/",
        {
            "nombre": "Camisa",
            "precio_monto": "10.00",
            "categoria_id": str(categoria.id),
            "tipo_producto_id": "tipo-inexistente",
        },
        format="json",
    )

    assert respuesta.status_code == 404
    assert "error" in respuesta.data
    assert PrendaModel.objects.count() == 0


@pytest.mark.parametrize(
    "tallas",
    [["UNICA"], ["ÚNICA"], ["40.5"], ["M", "m"], [""]],
)
def test_api_rechaza_tallas_invalidas(tallas, cliente_admin) -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas")
    cliente, _ = cliente_admin

    respuesta = cliente.post(
        "/api/prendas/",
        {
            "nombre": "Camisa",
            "precio_monto": "10.00",
            "categoria_id": str(categoria.id),
            "tallas": tallas,
        },
        format="json",
    )

    assert respuesta.status_code == 400
    assert PrendaModel.objects.count() == 0
