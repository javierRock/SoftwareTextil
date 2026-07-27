from decimal import Decimal

import pytest

from apps.catalogo.domain.prenda import PrendaFabrica
from apps.catalogo.tests.test_services import crear_servicio
from apps.compartido.domain.dinero import Dinero


def _prenda(
    nombre: str,
    descripcion: str,
    categoria_id: str,
    tipo_producto_id: str | None,
    activa: bool = True,
):
    prenda = PrendaFabrica.crear(
        nombre=nombre,
        descripcion=descripcion,
        precio=Dinero(Decimal("49.90"), "PEN"),
        categoria_id=categoria_id,
        tipo_producto_id=tipo_producto_id,
        registrado_por=None,
    )
    if not activa:
        prenda.desactivar()
    return prenda


def _servicio_con_prendas():
    servicio, repositorio, _ = crear_servicio()
    camisa = _prenda("Camisa clasica", "Algodon pima", "cat-1", "tipo-1")
    polo = _prenda("Polo basico", "Prenda de algodon", "cat-2", "tipo-2")
    inactiva = _prenda("Camisa retirada", "Seda", "cat-1", "tipo-1", activa=False)
    for prenda in (camisa, polo, inactiva):
        repositorio.guardar(prenda)
    return servicio, camisa, polo, inactiva


def test_filtros_vacios_conservan_el_listado_visible() -> None:
    servicio, camisa, polo, _ = _servicio_con_prendas()

    assert servicio.buscar_prendas(texto="", categoria_id="", estado="") == [
        camisa,
        polo,
    ]


def test_busca_texto_en_nombre_o_descripcion() -> None:
    servicio, camisa, polo, _ = _servicio_con_prendas()

    assert servicio.buscar_prendas(texto="CLASICA") == [camisa]
    assert servicio.buscar_prendas(texto="algodon") == [camisa, polo]


def test_filtra_por_categoria_tipo_y_estado() -> None:
    servicio, camisa, polo, inactiva = _servicio_con_prendas()

    assert servicio.buscar_prendas(categoria_id="cat-1") == [camisa]
    assert servicio.buscar_prendas(tipo_producto_id="tipo-2") == [polo]
    assert servicio.buscar_prendas(estado="inactiva") == [inactiva]


def test_combina_filtros_con_operador_y() -> None:
    servicio, camisa, _, _ = _servicio_con_prendas()

    assert servicio.buscar_prendas(
        texto="algodon",
        categoria_id="cat-1",
        tipo_producto_id="tipo-1",
        estado="activa",
    ) == [camisa]


def test_rechaza_estado_invalido() -> None:
    servicio, _, _, _ = _servicio_con_prendas()

    with pytest.raises(ValueError, match="estado de la prenda no es valido"):
        servicio.buscar_prendas(estado="agotada")
