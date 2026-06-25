from software_textil import create_app


def test_controlador_devuelve_400_si_falta_campo_requerido():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post("/inventario/stock", json={"stock_inicial": 1, "stock_minimo": 1})

    assert response.status_code == 400
    assert response.get_json()["error"] == "validation_error"


def test_controlador_devuelve_404_para_recurso_inexistente():
    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.post(
        "/inventario/salidas",
        json={
            "prenda_id": "no-existe",
            "cantidad": 1,
            "motivo": "venta",
            "usuario_id": "usuario-1",
        },
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "not_found"
