"""Garantiza rollback de todo el agregado cuando falla su persistencia."""

from unittest.mock import patch
from uuid import uuid4

import pytest

from apps.usuarios.domain.usuario import Rol
from apps.usuarios.infrastructure.repositories import DjangoRepositorioRol
from apps.usuarios.models import RolModel


@pytest.mark.django_db
def test_guardar_rol_revierte_nombre_si_falla_sincronizacion(crear_rol):
    modelo = crear_rol("Operador")
    rol = Rol(id=str(modelo.id), nombre="Supervisor")
    repo = DjangoRepositorioRol()

    with (
        patch.object(repo, "_sincronizar_permisos", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        repo.guardar(rol)

    modelo.refresh_from_db()
    assert modelo.nombre == "Operador"


@pytest.mark.django_db
def test_guardar_rol_nuevo_no_deja_fila_parcial_si_falla_sincronizacion():
    rol = Rol(id=str(uuid4()), nombre="Supervisor")
    repo = DjangoRepositorioRol()

    with (
        patch.object(repo, "_sincronizar_permisos", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        repo.guardar(rol)

    assert not RolModel.objects.filter(id=rol.id).exists()
