from decimal import Decimal

import pytest

from apps.catalogo.domain.prenda import PrendaFabrica
from apps.catalogo.tests.test_services import crear_servicio
from apps.compartido.domain.dinero import Dinero


def test_servicio_consulta_detalle_de_prenda_existente() -> None:
    servicio, repositorio, _ = crear_servicio()
    prenda = PrendaFabrica.crear(
        nombre="Camisa clasica",
        descripcion="Algodon",
        precio=Dinero(Decimal("49.90"), "PEN"),
        categoria_id="categoria-1",
        tipo_producto_id="tipo-1",
        registrado_por=None,
    )
    repositorio.guardar(prenda)

    assert servicio.buscar_prenda(prenda.id) == prenda


def test_servicio_controla_prenda_inexistente() -> None:
    servicio, _, _ = crear_servicio()

    with pytest.raises(ValueError, match="Prenda no encontrada"):
        servicio.buscar_prenda("inexistente")
