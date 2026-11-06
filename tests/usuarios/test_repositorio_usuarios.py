"""Suite de repositorio: usuarios y sesiones contra PostgreSQL (Lab 05).

Cada caso corre dentro de una transaccion que pytest-django revierte al
finalizar (TearDown automatico), asi los datos no se filtran entre pruebas.
"""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.compartido.domain.enums import EstadoSesion, EstadoUsuario
from apps.usuarios.domain.usuario import Rol, Sesion, UsuarioSistemaFabrica
from apps.usuarios.infrastructure.repositories import (
    DjangoRepositorioSesion,
    DjangoRepositorioUsuario,
)


@pytest.fixture
def rol_cliente(crear_rol) -> Rol:
    modelo = crear_rol("Cliente")
    return Rol(id=str(modelo.id), nombre=modelo.nombre)


@pytest.fixture
def repo_usuarios() -> DjangoRepositorioUsuario:
    return DjangoRepositorioUsuario()


@pytest.fixture
def usuario_guardado(repo_usuarios, rol_cliente):
    usuario = UsuarioSistemaFabrica.crear(
        nombre="Ana Torres",
        email=f"ana-{uuid4().hex[:6]}@textil.pe",
        username=f"ana-{uuid4().hex[:6]}",
        rol=rol_cliente,
    )
    repo_usuarios.guardar(usuario)
    return usuario


def _sesion(usuario_id: str, token: str) -> Sesion:
    return Sesion(
        id=str(uuid4()),
        usuario_id=usuario_id,
        token=token,
        fecha_inicio=timezone.now(),
        fecha_expiracion=timezone.now() + timedelta(hours=8),
        ip="",
    )


@pytest.mark.django_db
class TestDjangoRepositorioUsuario:
    def test_guardar_y_buscar_por_id(self, repo_usuarios, usuario_guardado) -> None:
        recuperado = repo_usuarios.buscar_por_id(usuario_guardado.id)

        assert recuperado.email == usuario_guardado.email
        assert recuperado.rol.nombre == "Cliente"

    def test_buscar_por_email_ignora_mayusculas(
        self, repo_usuarios, usuario_guardado
    ) -> None:
        recuperado = repo_usuarios.buscar_por_email(usuario_guardado.email.upper())
        assert recuperado.id == usuario_guardado.id

    def test_guardar_actualiza_estado(self, repo_usuarios, usuario_guardado) -> None:
        usuario_guardado.desactivar()
        repo_usuarios.guardar(usuario_guardado)

        recuperado = repo_usuarios.buscar_por_id(usuario_guardado.id)
        assert recuperado.estado == EstadoUsuario.INACTIVO

    def test_password_se_guarda_y_lee_por_id(
        self, repo_usuarios, usuario_guardado
    ) -> None:
        repo_usuarios.set_password(usuario_guardado.id, "hash-de-prueba")
        assert repo_usuarios.get_password_por_id(usuario_guardado.id) == (
            "hash-de-prueba"
        )

    def test_id_mal_formado_devuelve_none_y_password_vacio(self, repo_usuarios) -> None:
        assert repo_usuarios.buscar_por_id("abc") is None
        assert repo_usuarios.get_password_por_id("abc") == ""


@pytest.mark.django_db
class TestDjangoRepositorioSesion:
    def test_cerrar_otras_sesiones_conserva_la_actual(self, usuario_guardado) -> None:
        repo = DjangoRepositorioSesion()
        repo.guardar(_sesion(usuario_guardado.id, "token-actual"))
        repo.guardar(_sesion(usuario_guardado.id, "token-viejo"))

        repo.cerrar_por_usuario(usuario_guardado.id, excepto_token="token-actual")

        assert repo.buscar_por_token("token-actual").estado == EstadoSesion.ACTIVA
        assert repo.buscar_por_token("token-viejo").estado == EstadoSesion.CERRADA
