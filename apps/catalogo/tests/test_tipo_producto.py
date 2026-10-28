import pytest

from apps.catalogo.domain.excepciones import (
    RecursoNoEncontradoError,
    ValidacionError,
)
from apps.catalogo.domain.prenda import TipoProducto
from apps.catalogo.tests.test_services import crear_servicio


def test_tipo_producto_valida_y_normaliza_sus_datos() -> None:
    tipo = TipoProducto(
        id="tipo-1",
        nombre="  Camisa  ",
        atributos_base={"manga": "larga"},
    )

    assert tipo.nombre == "Camisa"
    assert tipo.atributos_base == {"manga": "larga"}
    assert tipo.activo is True


@pytest.mark.parametrize(
    ("nombre", "atributos_base"),
    [
        ("   ", {}),
        ("x" * 121, {}),
        ("Camisa", []),
        ("Camisa", {"": "larga"}),
        ("Camisa", {"manga": 1}),
    ],
)
def test_tipo_producto_rechaza_datos_invalidos(
    nombre,
    atributos_base,
) -> None:
    with pytest.raises(ValidacionError):
        TipoProducto(id="tipo-1", nombre=nombre, atributos_base=atributos_base)


def test_servicio_completa_el_ciclo_de_configuracion_de_tipos() -> None:
    servicio, _, _ = crear_servicio()
    tipo = servicio.crear_tipo_producto("Camisa", {"manga": "corta"})

    assert servicio.buscar_tipo(tipo.id) == tipo
    assert servicio.listar_tipos() == [tipo]

    actualizado = servicio.actualizar_tipo_producto(
        tipo.id,
        "Camisa formal",
        {"manga": "larga"},
    )
    assert actualizado.nombre == "Camisa formal"
    assert actualizado.atributos_base == {"manga": "larga"}

    assert servicio.desactivar_tipo_producto(tipo.id).activo is False
    assert servicio.activar_tipo_producto(tipo.id).activo is True


def test_servicio_controla_tipo_inexistente() -> None:
    servicio, _, _ = crear_servicio()

    with pytest.raises(RecursoNoEncontradoError):
        servicio.buscar_tipo("inexistente")
