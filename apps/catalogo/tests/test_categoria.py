import pytest

from apps.catalogo.domain.prenda import Categoria
from apps.catalogo.tests.test_services import crear_servicio


def test_categoria_valida_y_normaliza_sus_datos() -> None:
    categoria = Categoria(
        id="categoria-1",
        nombre="  Camisas  ",
        descripcion="  Prendas superiores  ",
    )

    assert categoria.nombre == "Camisas"
    assert categoria.descripcion == "Prendas superiores"


@pytest.mark.parametrize(
    ("nombre", "descripcion", "mensaje"),
    [
        ("   ", "", "El nombre de la categoria es obligatorio"),
        ("x" * 121, "", "no puede exceder 120 caracteres"),
        ("Camisas", None, "La descripcion de la categoria debe ser texto"),
    ],
)
def test_categoria_rechaza_datos_invalidos(nombre, descripcion, mensaje) -> None:
    with pytest.raises(ValueError, match=mensaje):
        Categoria(id="categoria-1", nombre=nombre, descripcion=descripcion)


def test_servicio_completa_creacion_consulta_y_actualizacion_de_categoria() -> None:
    servicio, _, _ = crear_servicio()

    categoria = servicio.crear_categoria("Camisas", "Prendas superiores")
    assert servicio.buscar_categoria(categoria.id) == categoria
    assert servicio.listar_categorias() == [categoria]

    actualizada = servicio.actualizar_categoria(
        categoria.id,
        "Camisas formales",
        "Camisas para ocasiones formales",
    )

    assert actualizada.nombre == "Camisas formales"
    assert actualizada.descripcion == "Camisas para ocasiones formales"


def test_servicio_no_persiste_categoria_invalida() -> None:
    servicio, _, repositorio = crear_servicio()

    with pytest.raises(ValueError, match="nombre de la categoria es obligatorio"):
        servicio.crear_categoria("   ")

    assert repositorio.categorias == {}


def test_servicio_controla_categoria_inexistente() -> None:
    servicio, _, _ = crear_servicio()

    with pytest.raises(ValueError, match="Categoria no encontrada"):
        servicio.buscar_categoria("inexistente")
