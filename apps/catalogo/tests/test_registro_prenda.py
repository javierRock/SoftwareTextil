from decimal import Decimal

import pytest

from apps.catalogo.domain.prenda import Categoria, PrendaFabrica, TipoProducto
from apps.catalogo.tests.test_services import crear_servicio
from apps.compartido.domain.dinero import Dinero


def test_fabrica_crea_ficha_comercial_valida() -> None:
    prenda = PrendaFabrica.crear(
        nombre="  Camisa clasica  ",
        descripcion="  Algodon  ",
        precio=Dinero(Decimal("49.90"), "PEN"),
        categoria_id="categoria-1",
        tipo_producto_id="tipo-1",
        registrado_por="usuario-externo",
    )

    assert prenda.nombre == "Camisa clasica"
    assert prenda.descripcion == "Algodon"
    assert prenda.precio == Dinero(Decimal("49.90"), "PEN")
    assert prenda.registrado_por == "usuario-externo"


@pytest.mark.parametrize(
    ("nombre", "descripcion", "precio", "mensaje"),
    [
        ("   ", "", Dinero(Decimal("10"), "PEN"), "nombre de la prenda es obligatorio"),
        ("Camisa", None, Dinero(Decimal("10"), "PEN"), "descripcion de la prenda debe ser texto"),
        ("Camisa", "", Dinero(Decimal("0"), "PEN"), "precio de la prenda debe ser mayor"),
        ("Camisa", "", Dinero(Decimal("10"), "pen"), "moneda debe ser un codigo"),
    ],
)
def test_fabrica_rechaza_ficha_comercial_invalida(
    nombre,
    descripcion,
    precio,
    mensaje,
) -> None:
    with pytest.raises(ValueError, match=mensaje):
        PrendaFabrica.crear(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria_id="categoria-1",
            registrado_por=None,
        )


def test_servicio_registra_prenda_con_categoria_y_tipo_existentes() -> None:
    servicio, repo_prenda, repo_catalogo = crear_servicio()
    repo_catalogo.guardar_categoria(Categoria(id="categoria-1", nombre="Camisas"))
    repo_catalogo.guardar_tipo_producto(TipoProducto(id="tipo-1", nombre="Camisa"))

    prenda = servicio.crear_prenda(
        nombre="Camisa clasica",
        descripcion="Algodon",
        precio_monto="49.90",
        precio_moneda="pen",
        categoria_id="categoria-1",
        tipo_producto_id="tipo-1",
        registrado_por="usuario-externo",
    )

    assert repo_prenda.prendas == {prenda.id: prenda}
    assert prenda.precio.moneda == "PEN"


def test_servicio_impide_registro_con_categoria_inexistente() -> None:
    servicio, repo_prenda, _ = crear_servicio()

    with pytest.raises(ValueError, match="La categoria no existe"):
        servicio.crear_prenda(
            nombre="Camisa",
            descripcion="",
            precio_monto="10",
            precio_moneda="PEN",
            categoria_id="inexistente",
            registrado_por=None,
        )

    assert repo_prenda.prendas == {}


def test_servicio_impide_registro_con_tipo_inexistente() -> None:
    servicio, repo_prenda, repo_catalogo = crear_servicio()
    repo_catalogo.guardar_categoria(Categoria(id="categoria-1", nombre="Camisas"))

    with pytest.raises(ValueError, match="El tipo de producto no existe"):
        servicio.crear_prenda(
            nombre="Camisa",
            descripcion="",
            precio_monto="10",
            precio_moneda="PEN",
            categoria_id="categoria-1",
            tipo_producto_id="inexistente",
            registrado_por=None,
        )

    assert repo_prenda.prendas == {}


@pytest.mark.parametrize("precio", ["0", "-1", "no-es-numero"])
def test_servicio_impide_registro_con_precio_invalido(precio) -> None:
    servicio, repo_prenda, repo_catalogo = crear_servicio()
    repo_catalogo.guardar_categoria(Categoria(id="categoria-1", nombre="Camisas"))

    with pytest.raises(ValueError):
        servicio.crear_prenda(
            nombre="Camisa",
            descripcion="",
            precio_monto=precio,
            precio_moneda="PEN",
            categoria_id="categoria-1",
            registrado_por=None,
        )

    assert repo_prenda.prendas == {}
