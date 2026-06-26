from software_textil import create_app


def test_flujo_checkout_http():
    app = create_app({"TESTING": True})
    client = app.test_client()

    carrito_response = client.post("/compras/carritos", json={"cliente_id": "cliente-1"})
    assert carrito_response.status_code == 201
    carrito_id = carrito_response.get_json()["id"]

    item_response = client.post(
        f"/compras/carritos/{carrito_id}/items",
        json={"prenda_id": "prenda-1", "cantidad": 2, "precio_unitario": "15.00"},
    )
    assert item_response.status_code == 201

    pedido_response = client.post("/pedidos", json={"carrito_id": carrito_id, "cliente_id": "cliente-1"})
    assert pedido_response.status_code == 201
    pedido = pedido_response.get_json()

    pago_response = client.post("/pagos", json={"pedido_id": pedido["id"], "monto": "30.00", "metodo": "yape"})
    assert pago_response.status_code == 201
    pago = pago_response.get_json()

    assert pedido["estado"] == "creado"
    assert pago["estado"] == "aprobado"
