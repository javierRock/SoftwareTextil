import pytest
from django.contrib.auth.hashers import check_password, make_password
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.usuarios.infrastructure.models import (
    IntentoLoginModel,
    RolModel,
    SesionModel,
    UsuarioModel,
)

pytestmark = pytest.mark.django_db
CLAVE = "ClaveSegura123!"


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def rol_cliente() -> RolModel:
    return RolModel.objects.get_or_create(
        nombre="Cliente",
        defaults={"descripcion": "Cliente ecommerce"},
    )[0]


@pytest.fixture
def rol_admin() -> RolModel:
    return RolModel.objects.get_or_create(
        nombre="Administrador",
        defaults={"descripcion": "Administrador del sistema"},
    )[0]


def crear_usuario(username: str, rol: RolModel, **datos) -> UsuarioModel:
    return UsuarioModel.objects.create(
        nombre=datos.get("nombre", username.title()),
        email=datos.get("email", f"{username}@example.com"),
        username=username,
        password_hash=make_password(datos.get("password", CLAVE)),
        estado=datos.get("estado", "activo"),
        rol=rol,
    )


def login(api_client: APIClient, username: str, password: str = CLAVE):
    return api_client.post(
        "/api/auth/login/",
        {"username": username, "password": password},
        format="json",
    )


def autenticar(api_client: APIClient, usuario: UsuarioModel) -> str:
    token = login(api_client, usuario.username).data["token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return token


def test_registro_publico_crea_cliente_con_password_hasheado(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    response = api_client.post(
        "/api/auth/registro/",
        {
            "nombre": "Carlos Gutierrez",
            "email": "CARLOS@example.com",
            "username": "Carlos",
            "password": CLAVE,
        },
        format="json",
    )

    assert response.status_code == 201
    usuario = UsuarioModel.objects.get(username="carlos")
    assert usuario.email == "carlos@example.com"
    assert usuario.rol == rol_cliente
    assert check_password(CLAVE, usuario.password_hash)


def test_registro_rechaza_identidad_duplicada_sin_importar_mayusculas(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    crear_usuario("carlos", rol_cliente)

    response = api_client.post(
        "/api/auth/registro/",
        {
            "nombre": "Otro Carlos",
            "email": "otro@example.com",
            "username": "CARLOS",
            "password": CLAVE,
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "Ya existe un usuario con ese username"


def test_login_crea_sesion_y_registra_intento_exitoso(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    crear_usuario("carlos", rol_cliente)

    response = login(api_client, "carlos")

    assert response.status_code == 200
    assert response.data["rol"] == "Cliente"
    assert SesionModel.objects.filter(
        token=response.data["token"],
        estado="activa",
    ).exists()
    assert IntentoLoginModel.objects.get(username="carlos").exitoso


def test_login_invalido_responde_401_y_audita_intento(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    crear_usuario("carlos", rol_cliente)

    response = login(api_client, "carlos", "clave-incorrecta")

    assert response.status_code == 401
    intento = IntentoLoginModel.objects.get(username="carlos")
    assert not intento.exitoso
    assert intento.motivo_fallo == "credenciales_invalidas"


def test_usuario_inactivo_no_puede_iniciar_sesion(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    crear_usuario("carlos", rol_cliente, estado="inactivo")

    response = login(api_client, "carlos")

    assert response.status_code == 403
    assert response.data["error"] == "Usuario inactivo"


def test_perfil_requiere_autenticacion(api_client: APIClient) -> None:
    response = api_client.get("/api/auth/perfil/")

    assert response.status_code == 403


def test_usuario_autenticado_consulta_y_actualiza_su_perfil(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    usuario = crear_usuario("carlos", rol_cliente)
    autenticar(api_client, usuario)

    consulta = api_client.get("/api/auth/perfil/")
    actualizacion = api_client.patch(
        "/api/auth/perfil/",
        {"nombre": "Carlos Enrique", "email": "nuevo@example.com"},
        format="json",
    )

    assert consulta.status_code == 200
    assert actualizacion.status_code == 200
    usuario.refresh_from_db()
    assert usuario.nombre == "Carlos Enrique"
    assert usuario.email == "nuevo@example.com"


def test_cambio_password_cierra_otras_sesiones(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    usuario = crear_usuario("carlos", rol_cliente)
    primera = login(api_client, "carlos").data["token"]
    segunda = login(api_client, "carlos").data["token"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {segunda}")

    response = api_client.post(
        "/api/auth/cambiar-password/",
        {"password_actual": CLAVE, "password_nuevo": "NuevaClave456!"},
        format="json",
    )

    assert response.status_code == 200
    assert SesionModel.objects.get(token=primera).estado == "cerrada"
    assert SesionModel.objects.get(token=segunda).estado == "activa"
    usuario.refresh_from_db()
    assert check_password("NuevaClave456!", usuario.password_hash)


def test_logout_invalida_token_actual(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    usuario = crear_usuario("carlos", rol_cliente)
    token = autenticar(api_client, usuario)

    response = api_client.post("/api/auth/logout/", {}, format="json")

    assert response.status_code == 200
    assert SesionModel.objects.get(token=token).estado == "cerrada"
    assert api_client.get("/api/auth/perfil/").status_code == 403


def test_cliente_no_puede_administrar_usuarios(
    api_client: APIClient,
    rol_cliente: RolModel,
) -> None:
    usuario = crear_usuario("cliente", rol_cliente)
    autenticar(api_client, usuario)

    assert api_client.get("/api/usuarios/").status_code == 403
    assert api_client.get("/api/roles/").status_code == 403


def test_administrador_crea_y_desactiva_usuario(
    api_client: APIClient,
    rol_admin: RolModel,
    rol_cliente: RolModel,
) -> None:
    administrador = crear_usuario("admin", rol_admin)
    autenticar(api_client, administrador)

    creacion = api_client.post(
        "/api/usuarios/",
        {
            "nombre": "Nuevo Cliente",
            "email": "nuevo@example.com",
            "username": "nuevo",
            "password": CLAVE,
            "rol_id": str(rol_cliente.id),
        },
        format="json",
    )
    desactivacion = api_client.post(
        f"/api/usuarios/{creacion.data['id']}/desactivar/",
        {},
        format="json",
    )

    assert creacion.status_code == 201
    assert desactivacion.status_code == 200
    assert UsuarioModel.objects.get(id=creacion.data["id"]).estado == "inactivo"


def test_administrador_no_puede_desactivarse(
    api_client: APIClient,
    rol_admin: RolModel,
) -> None:
    administrador = crear_usuario("admin", rol_admin)
    autenticar(api_client, administrador)

    response = api_client.post(
        f"/api/usuarios/{administrador.id}/desactivar/",
        {},
        format="json",
    )

    assert response.status_code == 409
    administrador.refresh_from_db()
    assert administrador.estado == "activo"


def test_comando_crear_admin_prepara_acceso_inicial(
    rol_admin: RolModel,
) -> None:
    call_command(
        "crear_admin",
        nombre="Administrador Inicial",
        email="admin@example.com",
        username="admin",
        password=CLAVE,
    )

    usuario = UsuarioModel.objects.get(username="admin")
    assert usuario.rol == rol_admin
    assert check_password(CLAVE, usuario.password_hash)
