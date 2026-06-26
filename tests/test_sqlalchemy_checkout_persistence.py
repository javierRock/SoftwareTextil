from software_textil import create_app
from software_textil.infrastructure.persistence.database import db
from software_textil.infrastructure.persistence.models import (
    CarritoModel,
    DetallePedidoModel,
    ItemCarritoModel,
    PagoModel,
    PedidoModel,
)
from software_textil.infrastructure.repositories.sqlalchemy_compras_repository import SQLAlchemyCarritoRepository
from software_textil.infrastructure.repositories.sqlalchemy_pagos_repository import SQLAlchemyPagoRepository
from software_textil.infrastructure.repositories.sqlalchemy_pedidos_repository import SQLAlchemyPedidoRepository
from software_textil.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


def _sqlalchemy_app():
    return create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "PERSISTENCE_BACKEND": "sqlalchemy",
            "CREATE_DATABASE": True,
        }
    )


def test_checkout_http_persiste_en_sqlalchemy():
    app = _sqlalchemy_app()
    client = app.test_client()

    carrito_response = client.post("/compras/carritos", json={"cliente_id": "cliente-sql"})
    assert carrito_response.status_code == 201
    carrito_id = carrito_response.get_json()["id"]

    item_response = client.post(
        f"/compras/carritos/{carrito_id}/items",
        json={"prenda_id": "prenda-sql", "cantidad": 2, "precio_unitario": "12.50"},
    )
    assert item_response.status_code == 201

    pedido_response = client.post("/pedidos", json={"carrito_id": carrito_id, "cliente_id": "cliente-sql"})
    assert pedido_response.status_code == 201
    pedido_id = pedido_response.get_json()["id"]

    pago_response = client.post("/pagos", json={"pedido_id": pedido_id, "monto": "25.00", "metodo": "tarjeta"})
    assert pago_response.status_code == 201

    with app.app_context():
        assert CarritoModel.query.count() == 1
        assert ItemCarritoModel.query.count() == 1
        assert PedidoModel.query.count() == 1
        assert DetallePedidoModel.query.count() == 1
        assert PagoModel.query.count() == 1
        assert db.session.get(PedidoModel, pedido_id).estado == "pagado"


def test_repositorios_sqlalchemy_recuperan_agregados_persistidos():
    app = _sqlalchemy_app()
    client = app.test_client()

    carrito_id = client.post("/compras/carritos", json={"cliente_id": "cliente-sql"}).get_json()["id"]
    client.post(
        f"/compras/carritos/{carrito_id}/items",
        json={"prenda_id": "prenda-sql", "cantidad": 1, "precio_unitario": "30.00"},
    )
    pedido_id = client.post("/pedidos", json={"carrito_id": carrito_id, "cliente_id": "cliente-sql"}).get_json()["id"]
    pago_id = client.post("/pagos", json={"pedido_id": pedido_id, "monto": "30.00", "metodo": "yape"}).get_json()["id"]

    with app.app_context():
        db.session.remove()
        carrito = SQLAlchemyCarritoRepository().buscar_por_id(carrito_id)
        pedido = SQLAlchemyPedidoRepository().buscar_por_id(pedido_id)
        pago = SQLAlchemyPagoRepository().buscar_por_id(pago_id)

        assert carrito is not None
        assert len(carrito.items) == 1
        assert pedido is not None
        assert pedido.estado == "pagado"
        assert pago is not None
        assert pago.metodo == "yape"


def test_sqlalchemy_unit_of_work_hace_rollback():
    app = _sqlalchemy_app()
    repositorio = SQLAlchemyCarritoRepository()
    uow = SQLAlchemyUnitOfWork()

    with app.app_context():
        with uow:
            from software_textil.domain.compras.carrito import CarritoFactory

            repositorio.guardar(CarritoFactory.crear("cliente-rollback"))
            uow.rollback()

        assert CarritoModel.query.count() == 0
