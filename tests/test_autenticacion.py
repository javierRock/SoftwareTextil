from software_textil.application.dtos.comandos import CrearUsuarioDTO, LoginDTO
from software_textil.application.services.servicio_autenticacion import ServicioAutenticacion
from software_textil.application.services.servicio_gestion_usuarios import ServicioGestionUsuarios
from software_textil.domain.compartido.enums import ResultadoLogin
from software_textil.infrastructure.repositories.in_memory import (
    InMemoryIntentoLoginRepository,
    InMemoryRolRepository,
    InMemorySesionRepository,
    InMemoryUsuarioRepository,
)
from software_textil.infrastructure.security import WorkzeugPasswordHasher


def test_usuario_creado_con_password_puede_autenticarse():
    usuarios = InMemoryUsuarioRepository()
    roles = InMemoryRolRepository()
    sesiones = InMemorySesionRepository()
    intentos = InMemoryIntentoLoginRepository()
    hasher = WorkzeugPasswordHasher()
    gestion_usuarios = ServicioGestionUsuarios(usuarios, roles, hasher)
    autenticacion = ServicioAutenticacion(usuarios, sesiones, intentos, hasher)

    rol = gestion_usuarios.crear_rol("admin")
    usuario = gestion_usuarios.crear_usuario(
        CrearUsuarioDTO(
            nombre="Admin",
            email="admin@example.com",
            rol_id=rol.id,
            password="secreto123",
        )
    )

    resultado, sesion = autenticacion.autenticar(LoginDTO(usuario.email, "secreto123", "127.0.0.1"))

    assert resultado == ResultadoLogin.EXITOSO
    assert sesion is not None
    assert usuario.credencial is not None
    assert usuario.credencial.password_hash != "secreto123"


def test_autenticacion_rechaza_password_incorrecto():
    usuarios = InMemoryUsuarioRepository()
    roles = InMemoryRolRepository()
    sesiones = InMemorySesionRepository()
    intentos = InMemoryIntentoLoginRepository()
    hasher = WorkzeugPasswordHasher()
    gestion_usuarios = ServicioGestionUsuarios(usuarios, roles, hasher)
    autenticacion = ServicioAutenticacion(usuarios, sesiones, intentos, hasher)

    rol = gestion_usuarios.crear_rol("admin")
    gestion_usuarios.crear_usuario(
        CrearUsuarioDTO(
            nombre="Admin",
            email="admin@example.com",
            rol_id=rol.id,
            password="secreto123",
        )
    )

    resultado, sesion = autenticacion.autenticar(LoginDTO("admin@example.com", "malo", "127.0.0.1"))

    assert resultado == ResultadoLogin.CREDENCIALES_INVALIDAS
    assert sesion is None
    assert len(intentos.items) == 1
