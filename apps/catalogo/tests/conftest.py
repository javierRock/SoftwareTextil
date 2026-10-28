import pytest
from rest_framework.test import APIClient

from apps.usuarios.presentation.authentication import UsuarioAutenticado


@pytest.fixture
def cliente_admin(crear_usuario):
    usuario = crear_usuario(nombre="Admin Catalogo", rol="Administrador")
    autenticado = UsuarioAutenticado(
        id=str(usuario.id),
        nombre=usuario.nombre,
        username=usuario.username,
        email=usuario.email,
        rol=usuario.rol.nombre,
    )
    cliente = APIClient()
    cliente.force_authenticate(user=autenticado)
    return cliente, usuario
