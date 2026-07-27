from decimal import Decimal

import pytest

from apps.catalogo.domain.prenda import PrendaFabrica
from apps.catalogo.tests.test_services import crear_servicio
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


def _crear_prenda():
    return PrendaFabrica.crear(
        nombre="Camisa clasica",
        descripcion="Algodon",
        precio=Dinero(Decimal("49.90"), "PEN"),
        categoria_id="categoria-1",
        tipo_producto_id="tipo-1",
        registrado_por=None,
    )


def test_servicio_desactiva_y_activa_una_prenda() -> None:
    servicio, repositorio, _ = crear_servicio()
    prenda = _crear_prenda()
    repositorio.guardar(prenda)

    desactivada = servicio.desactivar_prenda(prenda.id)
    assert desactivada.estado == EstadoPrenda.INACTIVA
    assert repositorio.buscar_por_id(prenda.id) == desactivada

    activada = servicio.activar_prenda(prenda.id)
    assert activada.estado == EstadoPrenda.ACTIVA
    assert repositorio.buscar_por_id(prenda.id) == activada


@pytest.mark.parametrize("operacion", ["activar_prenda", "desactivar_prenda"])
def test_servicio_controla_publicacion_de_prenda_inexistente(operacion) -> None:
    servicio, _, _ = crear_servicio()

    with pytest.raises(ValueError, match="Prenda no encontrada"):
        getattr(servicio, operacion)("inexistente")
