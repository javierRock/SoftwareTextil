"""Verifica que los invariantes del dominio vivan tambien en la base de datos.

Cada prueba intenta escribir una fila que el dominio prohibe y comprueba que
PostgreSQL la rechaza. Es la evidencia de que la integridad no depende solo del
codigo Python: aunque alguien escribiera por el ORM sin pasar por los agregados,
el esquema seguiria protegiendo el negocio.
"""

from decimal import Decimal
from uuid import uuid4

import pytest
from django.db import IntegrityError, connection, transaction

from apps.catalogo.models import VariantePrendaModel
from apps.inventario.models import StockVarianteModel
from apps.usuarios.models import UsuarioModel
from apps.ventas.models import CarritoModel, ItemCarritoModel, PedidoModel

pytestmark = pytest.mark.django_db


def test_pedido_exige_un_cliente_existente(crear_carrito) -> None:
    """Sin FK, la tabla admitia pedidos de clientes que no existen.

    Django declara las claves foraneas como `DEFERRABLE INITIALLY DEFERRED`,
    de modo que se validan al confirmar la transaccion. `check_constraints()`
    adelanta esa verificacion para poder afirmarla dentro de la prueba.
    """
    carrito = crear_carrito()

    def crear_pedido_huerfano() -> None:
        PedidoModel.objects.create(
            cliente_id=uuid4(),
            carrito=carrito,
            total_monto=Decimal("10.00"),
        )
        connection.check_constraints()

    with pytest.raises(IntegrityError), transaction.atomic():
        crear_pedido_huerfano()


def test_prenda_no_admite_dos_variantes_con_misma_talla_y_color(
    crear_prenda,
) -> None:
    prenda = crear_prenda()
    VariantePrendaModel.objects.create(
        prenda=prenda, sku="SKU-A", talla="M", color="AZUL"
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        VariantePrendaModel.objects.create(
            prenda=prenda, sku="SKU-B", talla="M", color="AZUL"
        )


def test_sku_es_unico_en_todo_el_catalogo(crear_prenda) -> None:
    VariantePrendaModel.objects.create(
        prenda=crear_prenda(), sku="SKU-UNICO", talla="M"
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        VariantePrendaModel.objects.create(
            prenda=crear_prenda(), sku="SKU-UNICO", talla="L"
        )


def test_stock_no_puede_quedar_negativo(crear_variante) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        StockVarianteModel.objects.create(
            variante=crear_variante(),
            cantidad_actual=-1,
            nivel_minimo=0,
        )


def test_stock_reservado_no_puede_exceder_al_disponible(crear_variante) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        StockVarianteModel.objects.create(
            variante=crear_variante(),
            cantidad_actual=5,
            cantidad_reservada=6,
            nivel_minimo=0,
        )


def test_una_variante_tiene_un_solo_registro_de_stock(crear_variante) -> None:
    variante = crear_variante()
    StockVarianteModel.objects.create(variante=variante, cantidad_actual=10)

    with pytest.raises(IntegrityError), transaction.atomic():
        StockVarianteModel.objects.create(variante=variante, cantidad_actual=3)


def test_un_cliente_solo_tiene_un_carrito_abierto(crear_usuario) -> None:
    cliente = crear_usuario()
    CarritoModel.objects.create(cliente=cliente, estado="abierto")

    with pytest.raises(IntegrityError), transaction.atomic():
        CarritoModel.objects.create(cliente=cliente, estado="abierto")


def test_el_historico_de_carritos_no_choca_con_la_unicidad(
    crear_usuario,
) -> None:
    """La unicidad es parcial: solo aplica a los carritos abiertos."""
    cliente = crear_usuario()
    CarritoModel.objects.create(cliente=cliente, estado="convertido")
    CarritoModel.objects.create(cliente=cliente, estado="convertido")
    CarritoModel.objects.create(cliente=cliente, estado="abierto")

    assert CarritoModel.objects.filter(cliente=cliente).count() == 3


def test_un_carrito_no_repite_la_misma_variante(
    crear_carrito,
    crear_variante,
) -> None:
    carrito = crear_carrito(estado="abierto")
    variante = crear_variante()
    ItemCarritoModel.objects.create(
        carrito=carrito, variante=variante, cantidad=1, precio_monto=Decimal("10.00")
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        ItemCarritoModel.objects.create(
            carrito=carrito,
            variante=variante,
            cantidad=2,
            precio_monto=Decimal("10.00"),
        )


def test_item_de_carrito_exige_cantidad_positiva(
    crear_carrito,
    crear_variante,
) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        ItemCarritoModel.objects.create(
            carrito=crear_carrito(estado="abierto"),
            variante=crear_variante(),
            cantidad=0,
            precio_monto=Decimal("10.00"),
        )


def test_pedido_rechaza_un_estado_fuera_del_enum(crear_usuario, crear_carrito) -> None:
    cliente = crear_usuario()
    with pytest.raises(IntegrityError), transaction.atomic():
        PedidoModel.objects.create(
            cliente=cliente,
            carrito=crear_carrito(cliente),
            total_monto=Decimal("10.00"),
            estado="entregado_ayer",
        )


def test_usuario_rechaza_un_estado_fuera_del_enum(crear_rol) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        UsuarioModel.objects.create(
            nombre="Fulano",
            email="fulano@textil.test",
            username="fulano",
            rol=crear_rol(),
            estado="suspendido",
        )


def test_username_es_unico_ignorando_mayusculas(crear_rol) -> None:
    rol = crear_rol()
    UsuarioModel.objects.create(
        nombre="Ana", email="ana@textil.test", username="ana", rol=rol
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        UsuarioModel.objects.create(
            nombre="Otra Ana", email="ana2@textil.test", username="ANA", rol=rol
        )
