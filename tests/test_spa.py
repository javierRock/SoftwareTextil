"""Integración entre las rutas Django y el frontend React."""

import pytest
from django.test import Client


@pytest.mark.parametrize(
    "ruta",
    ["/", "/login", "/catalogo", "/pedidos", "/inventario"],
)
def test_rutas_visuales_entregan_la_spa(ruta: str) -> None:
    respuesta = Client().get(ruta)

    assert respuesta.status_code == 200
    assert b'<div id="root">' in respuesta.content
    assert b"/static/zuren/assets/app.js" in respuesta.content


@pytest.mark.django_db
def test_fallback_spa_no_intercepta_la_api() -> None:
    respuesta = Client().get("/api/prendas/")

    assert respuesta.status_code == 200
    assert respuesta.headers["Content-Type"].startswith("application/json")
