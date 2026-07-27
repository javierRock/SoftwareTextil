"""Servicios de aplicacion para usuarios y autenticacion."""

from datetime import timedelta
from secrets import token_urlsafe
from uuid import uuid4

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone

from apps.compartido.domain.enums import EstadoSesion, EstadoUsuario, ResultadoLogin
from apps.usuarios.domain.exceptions import (
    CredencialesInvalidasError,
    OperacionNoPermitidaError,
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    UsuarioInactivoError,
)
from apps.usuarios.domain.repositorios import (
    RepositorioIntentoLogin,
    RepositorioRol,
    RepositorioSesion,
    RepositorioUsuario,
)
from apps.usuarios.domain.usuario import (
    IntentoLogin,
    Rol,
    Sesion,
    Usuario,
    UsuarioSistemaFabrica,
)

DURACION_SESION = timedelta(hours=8)
ROL_CLIENTE = "Cliente"


class ServicioAutenticacion:
    def __init__(
        self,
        repo_usuario: RepositorioUsuario,
        repo_sesion: RepositorioSesion,
        repo_intentos: RepositorioIntentoLogin,
    ) -> None:
        self.repo_usuario = repo_usuario
        self.repo_sesion = repo_sesion
        self.repo_intentos = repo_intentos

    def login(self, username: str, password: str, ip: str = "") -> dict:
        username = username.strip()
        usuario = self.repo_usuario.buscar_por_username(username)
        password_hash = self.repo_usuario.get_password(username)

        if usuario is None or not check_password(password, password_hash):
            self._registrar_intento(
                username,
                ip,
                False,
                ResultadoLogin.CREDENCIALES_INVALIDAS.value,
            )
            raise CredencialesInvalidasError("Credenciales invalidas")

        if usuario.estado == EstadoUsuario.INACTIVO:
            self._registrar_intento(
                username,
                ip,
                False,
                ResultadoLogin.USUARIO_INACTIVO.value,
            )
            raise UsuarioInactivoError("Usuario inactivo")

        self._registrar_intento(username, ip, True)

        token = token_urlsafe(32)
        sesion = Sesion(
            id=str(uuid4()),
            usuario_id=usuario.id,
            token=token,
            fecha_inicio=timezone.now(),
            fecha_expiracion=timezone.now() + DURACION_SESION,
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
            "expira_en": sesion.fecha_expiracion,
        }

    def logout(self, token: str) -> None:
        self.repo_sesion.cerrar_por_token(token)

    def cerrar_otras_sesiones(self, usuario_id: str, token_actual: str) -> None:
        self.repo_sesion.cerrar_por_usuario(usuario_id, excepto_token=token_actual)

    def _registrar_intento(
        self,
        username: str,
        ip: str,
        exitoso: bool,
        motivo: str | None = None,
    ) -> None:
        intento = IntentoLogin(
            id=str(uuid4()),
            username=username,
            fecha=timezone.now(),
            ip=ip,
            exitoso=exitoso,
            motivo_fallo=motivo,
        )
        self.repo_intentos.guardar(intento)


class ServicioGestionUsuarios:
    def __init__(
        self,
        repo_usuario: RepositorioUsuario,
        repo_rol: RepositorioRol,
    ) -> None:
        self.repo_usuario = repo_usuario
        self.repo_rol = repo_rol

    def crear_usuario(  # noqa: PLR0913, PLR0917
        self,
        nombre: str,
        email: str,
        rol_id: str,
        username: str,
        password: str,
        creado_por: str | None = None,
    ) -> Usuario:
        rol = self.repo_rol.buscar_por_id(rol_id)
        if rol is None:
            raise RecursoNoEncontradoError("El rol no existe")

        nombre, email, username = self._normalizar_datos(nombre, email, username)
        self._validar_unicidad(email, username)
        validate_password(password)

        usuario = UsuarioSistemaFabrica.crear(
            nombre=nombre,
            email=email,
            username=username,
            rol=rol,
            creado_por=creado_por,
        )
        self.repo_usuario.guardar(usuario)
        self.repo_usuario.set_password(usuario.id, make_password(password))
        return usuario

    def registrar_cliente(
        self,
        nombre: str,
        email: str,
        username: str,
        password: str,
    ) -> Usuario:
        rol = self.repo_rol.buscar_por_nombre(ROL_CLIENTE)
        if rol is None:
            raise RecursoNoEncontradoError("El rol Cliente no esta configurado")
        return self.crear_usuario(
            nombre=nombre,
            email=email,
            rol_id=rol.id,
            username=username,
            password=password,
        )

    def actualizar_perfil(
        self,
        usuario_id: str,
        nombre: str,
        email: str,
    ) -> Usuario:
        usuario = self._obtener_usuario(usuario_id)
        nombre = nombre.strip()
        email = email.strip().lower()
        if not nombre:
            raise OperacionNoPermitidaError("El nombre es obligatorio")
        usuario_con_email = self.repo_usuario.buscar_por_email(email)
        if usuario_con_email and usuario_con_email.id != usuario_id:
            raise RecursoDuplicadoError("Ya existe un usuario con ese email")
        usuario.actualizar_perfil(nombre, email)
        self.repo_usuario.guardar(usuario)
        return usuario

    def cambiar_password(
        self,
        usuario_id: str,
        password_actual: str,
        password_nuevo: str,
    ) -> None:
        usuario = self._obtener_usuario(usuario_id)
        password_hash = self.repo_usuario.get_password_por_id(usuario_id)
        if not check_password(password_actual, password_hash):
            raise CredencialesInvalidasError("La contrasena actual no es correcta")
        if check_password(password_nuevo, password_hash):
            raise OperacionNoPermitidaError(
                "La nueva contrasena debe ser diferente a la actual"
            )
        validate_password(password_nuevo, user=None)
        self.repo_usuario.set_password(usuario.id, make_password(password_nuevo))

    def listar_usuarios(self) -> list[Usuario]:
        return self.repo_usuario.listar()

    def buscar_usuario(self, usuario_id: str) -> Usuario | None:
        return self.repo_usuario.buscar_por_id(usuario_id)

    def desactivar_usuario(self, usuario_id: str) -> None:
        usuario = self._obtener_usuario(usuario_id)
        usuario.desactivar()
        self.repo_usuario.guardar(usuario)

    def activar_usuario(self, usuario_id: str) -> None:
        usuario = self._obtener_usuario(usuario_id)
        usuario.activar()
        self.repo_usuario.guardar(usuario)

    def crear_rol(self, nombre: str, descripcion: str = "") -> Rol:
        nombre = nombre.strip()
        if not nombre:
            raise OperacionNoPermitidaError("El nombre del rol es obligatorio")
        if self.repo_rol.buscar_por_nombre(nombre):
            raise RecursoDuplicadoError("Ya existe un rol con ese nombre")
        rol = Rol(id=str(uuid4()), nombre=nombre, descripcion=descripcion.strip())
        self.repo_rol.guardar(rol)
        return rol

    def listar_roles(self) -> list[Rol]:
        return self.repo_rol.listar()

    def _obtener_usuario(self, usuario_id: str) -> Usuario:
        usuario = self.repo_usuario.buscar_por_id(usuario_id)
        if usuario is None:
            raise RecursoNoEncontradoError("Usuario no encontrado")
        return usuario

    def _validar_unicidad(self, email: str, username: str) -> None:
        if self.repo_usuario.buscar_por_email(email) is not None:
            raise RecursoDuplicadoError("Ya existe un usuario con ese email")
        if self.repo_usuario.buscar_por_username(username) is not None:
            raise RecursoDuplicadoError("Ya existe un usuario con ese username")

    @staticmethod
    def _normalizar_datos(
        nombre: str,
        email: str,
        username: str,
    ) -> tuple[str, str, str]:
        return nombre.strip(), email.strip().lower(), username.strip().lower()
