"""S-03 (#65): las rutas de ventas comparten prefijo y conservan su orden.

Carrito, pedidos, pagos y despachos se publican bajo `/api/ventas/`, en ese
orden y antes del fallback de la SPA, declarando el prefijo una sola vez.
"""

from pathlib import Path

import pytest
from django.urls import URLResolver, resolve, reverse

from config import urls

RUTAS_VENTAS = [
    ("carritos-list", "/api/ventas/carritos/", "apps.ventas.carrito"),
    ("pedidos-list", "/api/ventas/pedidos/", "apps.ventas.pedidos"),
    ("pagos-list", "/api/ventas/pagos/", "apps.ventas.pagos"),
    ("despachos-list", "/api/ventas/despachos/", "apps.ventas.despachos"),
]
MODULOS_EN_ORDEN = [f"{paquete}.presentation.urls" for _, _, paquete in RUTAS_VENTAS]


def _modulos_incluidos_bajo(prefijo: str) -> list[str]:
    return [
        patron.urlconf_module.__name__
        for patron in urls.urlpatterns
        if isinstance(patron, URLResolver) and str(patron.pattern) == prefijo
    ]


@pytest.mark.parametrize(("nombre", "ruta", "paquete"), RUTAS_VENTAS)
def test_cada_modulo_de_ventas_se_publica_bajo_el_prefijo(
    nombre: str, ruta: str, paquete: str
) -> None:
    coincidencia = resolve(ruta)

    assert reverse(nombre) == ruta
    assert coincidencia.func.__module__.startswith(paquete)


def test_modulos_de_ventas_conservan_su_orden_de_inclusion() -> None:
    assert _modulos_incluidos_bajo("api/ventas/") == MODULOS_EN_ORDEN


def test_rutas_de_ventas_se_resuelven_antes_del_fallback_de_la_spa() -> None:
    nombres = [getattr(patron, "name", None) for patron in urls.urlpatterns]
    ultimo_indice_ventas = max(
        indice
        for indice, patron in enumerate(urls.urlpatterns)
        if isinstance(patron, URLResolver) and str(patron.pattern) == "api/ventas/"
    )

    assert ultimo_indice_ventas < nombres.index("spa")


def test_el_prefijo_de_ventas_se_declara_una_sola_vez() -> None:
    fuente = Path(urls.__file__).read_text(encoding="utf-8")

    assert fuente.count('"api/ventas/"') == 1
    assert fuente.count("path(RUTA_VENTAS") == 1
