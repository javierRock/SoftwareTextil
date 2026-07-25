"""Agregado de usuarios, roles y autenticacion."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from apps.compartido.domain.enums import EstadoSesion, EstadoUsuario


@dataclass
class Permiso:
    id: str
    codigo: str
    descripcion: str
    modulo: str


@dataclass
class Rol:
    id: str
    nombre: str
    descripcion: str = ""
    permisos: list[Permiso] = field(default_factory=list)

    def asignar_permiso(self, permiso: Permiso) -> None:
        if permiso not in self.permisos:
            self.permisos.append(permiso)


@dataclass
class Credencial:
    username: str
    password_hash: str
    salt: str
    algoritmo_hash: str = "werkzeug-pbkdf2"
    ultimo_cambio: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Sesion:
    id: str
    usuario_id: str
    token: str
    fecha_inicio: datetime
    fecha_expiracion: datetime
    ip: str
    estado: EstadoSesion = EstadoSesion.ACTIVA

    def cerrar(self) -> None:
        self.estado = EstadoSesion.CERRADA

    def esta_activa(self, ahora: datetime | None = None) -> bool:
        momento = ahora or datetime.now(UTC)
        return self.estado == EstadoSesion.ACTIVA and momento < self.fecha_expiracion


@dataclass
class IntentoLogin:
    id: str
    username: str
    fecha: datetime
    ip: str
    exitoso: bool
    motivo_fallo: str | None = None


@dataclass
class Usuario:
    id: str
    nombre: str
    email: str
    username: str
    rol: Rol
    estado: EstadoUsuario = EstadoUsuario.ACTIVO
    credencial: Credencial | None = None
    creado_por: str | None = None
    fecha_creacion: datetime = field(default_factory=lambda: datetime.now(UTC))

    def desactivar(self) -> None:
        self.estado = EstadoUsuario.INACTIVO

    def activar(self) -> None:
        self.estado = EstadoUsuario.ACTIVO

    def asignar_rol(self, rol: Rol) -> None:
        self.rol = rol

    def actualizar_perfil(self, nombre: str, email: str) -> None:
        self.nombre = nombre.strip()
        self.email = email.strip().lower()


class UsuarioSistemaFabrica:
    @staticmethod
    def crear(
        nombre: str,
        email: str,
        username: str,
        rol: Rol,
        creado_por: str | None = None,
    ) -> Usuario:
        return Usuario(
            id=str(uuid4()),
            nombre=nombre,
            email=email,
            username=username,
            rol=rol,
            creado_por=creado_por,
        )
