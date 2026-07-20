import pytest
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient

from apps.usuarios.infrastructure.models import IntentoLoginModel, RolModel, SesionModel, UsuarioModel


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def rol_cliente() -> RolModel:
    return RolModel.objects.create(nombre="Cliente", descripcion="Cliente ecommerce")


def test_registra_usuario_con_password_hasheado(api_client: APIClient, rol_cliente: RolModel) -> None:
    response = api_client.post(
        "/api/usuarios/",
        {
            "nombre": "Carlos Gutierrez",
            "email": "carlos@example.com",
            "username": "carlos",
            "password": "ClaveSegura123!",
            "rol_id": str(rol_cliente.id),
        },
        format="json",
    )

    assert response.status_code == 201
    usuario = UsuarioModel.objects.get(username="carlos")
    assert usuario.email == "carlos@example.com"
    assert usuario.password_hash
    assert usuario.password_hash != "ClaveSegura123!"


def test_rechaza_username_duplicado(api_client: APIClient, rol_cliente: RolModel) -> None:
    UsuarioModel.objects.create(
        nombre="Carlos",
        email="carlos@example.com",
        username="carlos",
        password_hash=make_password("ClaveSegura123!"),
        rol=rol_cliente,
    )

    response = api_client.post(
        "/api/usuarios/",
        {
            "nombre": "Carlos 2",
            "email": "carlos2@example.com",
            "username": "carlos",
            "password": "ClaveSegura123!",
            "rol_id": str(rol_cliente.id),
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"] == "Ya existe un usuario con ese username"


def test_login_crea_sesion_activa(api_client: APIClient, rol_cliente: RolModel) -> None:
    UsuarioModel.objects.create(
        nombre="Carlos",
        email="carlos@example.com",
        username="carlos",
        password_hash=make_password("ClaveSegura123!"),
        rol=rol_cliente,
    )

    response = api_client.post(
        "/api/auth/login/",
        {"username": "carlos", "password": "ClaveSegura123!"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["token"]
    assert response.data["rol"] == "Cliente"
    assert SesionModel.objects.filter(token=response.data["token"], estado="activa").exists()


def test_login_fallido_registra_intento(api_client: APIClient, rol_cliente: RolModel) -> None:
    UsuarioModel.objects.create(
        nombre="Carlos",
        email="carlos@example.com",
        username="carlos",
        password_hash=make_password("ClaveSegura123!"),
        rol=rol_cliente,
    )

    response = api_client.post(
        "/api/auth/login/",
        {"username": "carlos", "password": "clave-incorrecta"},
        format="json",
    )

    assert response.status_code == 400
    intento = IntentoLoginModel.objects.get(username="carlos")
    assert not intento.exitoso
    assert intento.motivo_fallo == "credenciales_invalidas"


def test_logout_cierra_sesion(api_client: APIClient, rol_cliente: RolModel) -> None:
    UsuarioModel.objects.create(
        nombre="Carlos",
        email="carlos@example.com",
        username="carlos",
        password_hash=make_password("ClaveSegura123!"),
        rol=rol_cliente,
    )
    login_response = api_client.post(
        "/api/auth/login/",
        {"username": "carlos", "password": "ClaveSegura123!"},
        format="json",
    )
    token = login_response.data["token"]

    response = api_client.post("/api/auth/logout/", {"token": token}, format="json")

    assert response.status_code == 200
    assert SesionModel.objects.get(token=token).estado == "cerrada"
