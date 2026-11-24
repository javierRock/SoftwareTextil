"""S-02 (#64): una sola referencia compartida al modelo de usuario.

Las claves foraneas hacia `UsuarioModel` de catalogo, inventario y ventas
deben apuntar al mismo modelo usando la constante compartida, sin repetir el
literal y sin generar migraciones nuevas.
"""

from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command

from apps.catalogo.models import PrendaModel
from apps.compartido.infrastructure.models import MODELO_USUARIO
from apps.inventario.models import MovimientoInventarioModel
from apps.usuarios.models import UsuarioModel
from apps.ventas.models import CarritoModel, DespachoModel, PedidoModel

RAIZ_APPS = Path(__file__).resolve().parents[2] / "apps"
MODULOS_CON_REFERENCIA = ("catalogo", "inventario", "ventas")

CLAVES_FORANEAS_A_USUARIO = [
    (CarritoModel, "cliente"),
    (PedidoModel, "cliente"),
    (DespachoModel, "responsable"),
    (PrendaModel, "registrado_por"),
    (MovimientoInventarioModel, "registrado_por"),
]


def test_la_constante_compartida_identifica_al_modelo_de_usuario() -> None:
    assert UsuarioModel._meta.label == MODELO_USUARIO


@pytest.mark.parametrize(("modelo", "campo"), CLAVES_FORANEAS_A_USUARIO)
def test_clave_foranea_apunta_al_modelo_de_usuario(modelo, campo) -> None:
    relacion = modelo._meta.get_field(campo)

    assert relacion.related_model is UsuarioModel


@pytest.mark.parametrize("modulo", MODULOS_CON_REFERENCIA)
def test_modelos_no_repiten_el_literal_del_usuario(modulo: str) -> None:
    fuente = (RAIZ_APPS / modulo / "models.py").read_text(encoding="utf-8")

    assert f'"{MODELO_USUARIO}"' not in fuente


@pytest.mark.django_db
def test_la_referencia_compartida_no_requiere_migraciones() -> None:
    salida = StringIO()

    call_command(
        "makemigrations",
        "catalogo",
        "inventario",
        "ventas",
        check=True,
        dry_run=True,
        stdout=salida,
    )

    assert "No changes detected" in salida.getvalue()
