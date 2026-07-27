"""Fixtures compartidas por toda la suite.

El esquema tiene integridad referencial real, asi que una prueba ya no puede
inventar identificadores: necesita filas de verdad. Estas fabricas las crean
con el minimo de datos y un sufijo aleatorio, para que cada prueba sea
independiente de las demas.
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from apps.catalogo.models import CategoriaModel, PrendaModel, VariantePrendaModel
from apps.usuarios.models import RolModel, UsuarioModel
from apps.ventas.models import CarritoModel, PedidoModel


def _sufijo() -> str:
    return uuid4().hex[:10]


@pytest.fixture
def crear_rol(db):
    def _crear_rol(nombre: str = "Cliente") -> RolModel:
        rol, _ = RolModel.objects.get_or_create(
            nombre=nombre,
            defaults={"descripcion": f"Rol {nombre}"},
        )
        return rol

    return _crear_rol


@pytest.fixture
def crear_usuario(db, crear_rol):
    def _crear_usuario(nombre: str = "Usuario", rol: str = "Cliente") -> UsuarioModel:
        sufijo = _sufijo()
        return UsuarioModel.objects.create(
            nombre=nombre,
            email=f"{sufijo}@textil.test",
            username=f"usuario-{sufijo}",
            rol=crear_rol(rol),
        )

    return _crear_usuario


@pytest.fixture
def crear_categoria(db):
    def _crear_categoria(nombre: str | None = None) -> CategoriaModel:
        return CategoriaModel.objects.create(nombre=nombre or f"Categoria {_sufijo()}")

    return _crear_categoria


@pytest.fixture
def crear_prenda(db, crear_categoria):
    def _crear_prenda(precio: str = "59.90") -> PrendaModel:
        return PrendaModel.objects.create(
            nombre=f"Prenda {_sufijo()}",
            descripcion="Prenda de prueba",
            precio_monto=Decimal(precio),
            precio_moneda="PEN",
            categoria=crear_categoria(),
        )

    return _crear_prenda


@pytest.fixture
def crear_variante(db, crear_prenda):
    def _crear_variante(
        prenda: PrendaModel | None = None,
        talla: str = "M",
        color: str = "",
    ) -> VariantePrendaModel:
        prenda = prenda or crear_prenda()
        return VariantePrendaModel.objects.create(
            prenda=prenda,
            sku=f"SKU-{_sufijo()}",
            talla=talla,
            color=color,
        )

    return _crear_variante


@pytest.fixture
def crear_carrito(db, crear_usuario):
    def _crear_carrito(
        cliente: UsuarioModel | None = None,
        estado: str = "convertido",
    ) -> CarritoModel:
        return CarritoModel.objects.create(
            cliente=cliente or crear_usuario(),
            estado=estado,
        )

    return _crear_carrito


@pytest.fixture
def crear_pedido(db, crear_usuario, crear_carrito):
    def _crear_pedido(
        cliente: UsuarioModel | None = None,
        total: str = "120.50",
    ) -> PedidoModel:
        cliente = cliente or crear_usuario()
        return PedidoModel.objects.create(
            cliente=cliente,
            carrito=crear_carrito(cliente),
            total_monto=Decimal(total),
            total_moneda="PEN",
        )

    return _crear_pedido
