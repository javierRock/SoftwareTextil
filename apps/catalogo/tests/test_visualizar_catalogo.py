from decimal import Decimal

from apps.catalogo.domain.prenda import PrendaFabrica
from apps.catalogo.tests.test_services import crear_servicio
from apps.compartido.domain.dinero import Dinero


def _crear_prenda(nombre: str):
    return PrendaFabrica.crear(
        nombre=nombre,
        descripcion="Algodon",
        precio=Dinero(Decimal("49.90"), "PEN"),
        categoria_id="categoria-1",
        tipo_producto_id="tipo-1",
        registrado_por=None,
    )


def test_servicio_devuelve_catalogo_vacio() -> None:
    servicio, _, _ = crear_servicio()

    assert servicio.listar_catalogo() == []


def test_servicio_devuelve_solo_prendas_visibles() -> None:
    servicio, repositorio, _ = crear_servicio()
    visible = _crear_prenda("Camisa visible")
    inactiva = _crear_prenda("Camisa inactiva")
    inactiva.desactivar()
    repositorio.guardar(visible)
    repositorio.guardar(inactiva)

    assert servicio.listar_catalogo() == [visible]
