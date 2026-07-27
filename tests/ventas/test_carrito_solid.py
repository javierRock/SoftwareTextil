"""Pruebas del modulo de carrito que evidencian LSP, ISP y DIP.

Los casos de uso se ejercitan contra el repositorio en memoria: si pasan sin
tocar la base de datos, es porque el servicio depende del contrato y no de la
implementacion Django.
"""

import pytest

from apps.compartido.domain.enums import EstadoCarrito
from apps.ventas.carrito.application.consultas import ConsultaCarritos
from apps.ventas.carrito.application.services import ServicioCompras
from apps.ventas.carrito.domain.errors import (
    CarritoNoEncontradoError,
    ItemInexistenteError,
)
from apps.ventas.carrito.domain.repositorios import (
    CatalogoCarritos,
    EscritorCarrito,
    LectorCarrito,
    RepositorioCarrito,
)
from apps.ventas.carrito.infrastructure.memoria import MemoriaRepositorioCarrito


@pytest.fixture
def repositorio() -> MemoriaRepositorioCarrito:
    return MemoriaRepositorioCarrito()


@pytest.fixture
def servicio(repositorio: MemoriaRepositorioCarrito) -> ServicioCompras:
    return ServicioCompras(lector=repositorio, escritor=repositorio)


@pytest.fixture
def consulta(repositorio: MemoriaRepositorioCarrito) -> ConsultaCarritos:
    return ConsultaCarritos(lector=repositorio, catalogo=repositorio)


def test_el_doble_en_memoria_satisface_los_contratos_segregados(repositorio):
    """LSP + ISP: una sola clase cubre los tres roles del contrato."""
    assert isinstance(repositorio, RepositorioCarrito)
    assert isinstance(repositorio, LectorCarrito)
    assert isinstance(repositorio, CatalogoCarritos)
    assert isinstance(repositorio, EscritorCarrito)


def test_agregar_item_acumula_cantidad_y_totaliza(servicio, consulta):
    carrito = servicio.crear_carrito(cliente_id="cliente-1")

    servicio.agregar_item(carrito.id, "prenda-1", 2, "25.00")
    servicio.agregar_item(carrito.id, "prenda-1", 3, "25.00")

    guardado = consulta.obtener(carrito.id)
    assert len(guardado.items) == 1
    assert guardado.items[0].cantidad == 5
    assert guardado.total().monto == 125


def test_quitar_item_inexistente_lanza_error_de_dominio(servicio):
    carrito = servicio.crear_carrito(cliente_id="cliente-1")

    with pytest.raises(ItemInexistenteError):
        servicio.quitar_item(carrito.id, "prenda-fantasma")


def test_operar_sobre_carrito_inexistente_lanza_error_de_dominio(servicio):
    with pytest.raises(CarritoNoEncontradoError):
        servicio.agregar_item("carrito-fantasma", "prenda-1", 1, "10.00")


def test_consulta_filtra_por_cliente(servicio, consulta):
    servicio.crear_carrito(cliente_id="cliente-1")
    servicio.crear_carrito(cliente_id="cliente-2")

    assert len(consulta.listar()) == 2
    assert len(consulta.listar("cliente-1")) == 1


def test_carrito_nuevo_nace_abierto_y_vacio(servicio):
    carrito = servicio.crear_carrito(cliente_id="cliente-1")

    assert carrito.estado is EstadoCarrito.ABIERTO
    assert carrito.items == []
