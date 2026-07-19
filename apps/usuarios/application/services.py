"""Servicios de aplicacion para usuarios y autenticacion."""

from datetime import datetime, timedelta
from uuid import uuid4

from django.contrib.auth.hashers import check_password, make_password

from apps.compartido.domain.enums import EstadoSesion, ResultadoLogin
from apps.usuarios.domain.usuario import (
    IntentoLogin,
    Rol,
    Sesion,
    Usuario,
    UsuarioSistemaFabrica,
)
from apps.usuarios.infrastructure.repositories import (
    DjangoRepositorioIntentoLogin,
    DjangoRepositorioRol,
    DjangoRepositorioSesion,
    DjangoRepositorioUsuario,
)


class ServicioAutenticacion:
    def __init__(
        self,
        repo_usuario: DjangoRepositorioUsuario,
        repo_sesion: DjangoRepositorioSesion,
        repo_intentos: DjangoRepositorioIntentoLogin,
    ) -> None:
        self.repo_usuario = repo_usuario
        self.repo_sesion = repo_sesion
        self.repo_intentos = repo_intentos

    def login(self, username: str, password: str, ip: str = "") -> dict:
        usuario = self.repo_usuario.buscar_por_username(username)
        password_hash = self.repo_usuario.get_password(username)

        if usuario is None or not check_password(password, password_hash):
            self._registrar_intento(username, ip, False, ResultadoLogin.CREDENCIALES_INVALIDAS.value)
            raise ValueError("Credenciales invalidas")

        if usuario.estado.value == "inactivo":
            self._registrar_intento(username, ip, False, ResultadoLogin.USUARIO_INACTIVO.value)
            raise ValueError("Usuario inactivo")

        self._registrar_intento(username, ip, True)

        token = str(uuid4())
        sesion = Sesion(
            id=str(uuid4()),
            usuario_id=usuario.id,
            token=token,
            fecha_inicio=datetime.utcnow(),
            fecha_expiracion=datetime.utcnow() + timedelta(hours=8),
            ip=ip,
            estado=EstadoSesion.ACTIVA,
        )
        self.repo_sesion.guardar(sesion)

        return {
            "token": token,
            "usuario_id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol.nombre,
        }

    def logout(self, token: str) -> None:
        self.repo_sesion.cerrar_por_token(token)

    def _registrar_intento(self, username: str, ip: str, exitoso: bool, motivo: str | None = None) -> None:
        intento = IntentoLogin(
            id=str(uuid4()),
            username=username,
            fecha=datetime.utcnow(),
            ip=ip,
            exitoso=exitoso,
            motivo_fallo=motivo,
        )
        self.repo_intentos.guardar(intento)


class ServicioGestionUsuarios:
    def __init__(
        self,
        repo_usuario: DjangoRepositorioUsuario,
        repo_rol: DjangoRepositorioRol,
    ) -> None:
        self.repo_usuario = repo_usuario
        self.repo_rol = repo_rol

    def crear_usuario(self, nombre: str, email: str, rol_id: str, username: str, password: str, creado_por: str | None = None) -> Usuario:
        rol = self.repo_rol.buscar_por_id(rol_id)
        if rol is None:
            raise ValueError("El rol no existe")

        if self.repo_usuario.buscar_por_email(email) is not None:
            raise ValueError("Ya existe un usuario con ese email")

        usuario = UsuarioSistemaFabrica.crear(nombre=nombre, email=email, rol=rol, creado_por=creado_por)
        self.repo_usuario.guardar(usuario)
        self.repo_usuario.set_password(usuario.id, make_password(password))

        from apps.usuarios.infrastructure.models import UsuarioModel
        UsuarioModel.objects.filter(id=usuario.id).update(username=username)
        return usuario

    def listar_usuarios(self) -> list[Usuario]:
        return self.repo_usuario.listar()

    def buscar_usuario(self, usuario_id: str) -> Usuario | None:
        return self.repo_usuario.buscar_por_id(usuario_id)

    def desactivar_usuario(self, usuario_id: str) -> None:
        usuario = self.repo_usuario.buscar_por_id(usuario_id)
        if usuario is None:
            raise ValueError("Usuario no encontrado")
        usuario.desactivar()
        self.repo_usuario.guardar(usuario)

    def crear_rol(self, nombre: str, descripcion: str = "") -> Rol:
        rol = Rol(id=str(uuid4()), nombre=nombre, descripcion=descripcion)
        self.repo_rol.guardar(rol)
        return rol

    def listar_roles(self) -> list:
        return self.repo_rol.listar()
