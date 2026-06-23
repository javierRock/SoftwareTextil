"""Casos de uso de autenticacion."""

from datetime import datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import uuid4

from software_textil.application.dtos.comandos import LoginDTO
from software_textil.domain.compartido.enums import EstadoUsuario, ResultadoLogin
from software_textil.domain.usuarios.repositorios import RepositorioIntentoLogin, RepositorioSesion, RepositorioUsuario
from software_textil.domain.usuarios.usuario import IntentoLogin, Sesion


class ServicioAutenticacion:
    def __init__(
        self,
        usuarios: RepositorioUsuario,
        sesiones: RepositorioSesion,
        intentos: RepositorioIntentoLogin,
    ) -> None:
        self.usuarios = usuarios
        self.sesiones = sesiones
        self.intentos = intentos

    def autenticar(self, dto: LoginDTO) -> tuple[ResultadoLogin, Sesion | None]:
        usuario = self.usuarios.buscar_por_email(dto.username)
        if usuario is None or usuario.credencial is None:
            self._registrar_intento(dto, False, "usuario_no_encontrado")
            return ResultadoLogin.CREDENCIALES_INVALIDAS, None
        if usuario.estado != EstadoUsuario.ACTIVO:
            self._registrar_intento(dto, False, "usuario_inactivo")
            return ResultadoLogin.USUARIO_INACTIVO, None
        if self._hash_password(dto.password, usuario.credencial.salt) != usuario.credencial.password_hash:
            self._registrar_intento(dto, False, "password_incorrecto")
            return ResultadoLogin.CREDENCIALES_INVALIDAS, None

        sesion = Sesion(
            id=str(uuid4()),
            usuario_id=usuario.id,
            token=token_urlsafe(32),
            fecha_inicio=datetime.utcnow(),
            fecha_expiracion=datetime.utcnow() + timedelta(hours=8),
            ip=dto.ip,
        )
        self.sesiones.guardar(sesion)
        self._registrar_intento(dto, True, None)
        return ResultadoLogin.EXITOSO, sesion

    def cerrar_sesion(self, token: str) -> None:
        sesion = self.sesiones.buscar_por_token(token)
        if sesion is not None:
            sesion.cerrar()
            self.sesiones.guardar(sesion)

    def validar_sesion(self, token: str) -> bool:
        sesion = self.sesiones.buscar_por_token(token)
        return bool(sesion and sesion.esta_activa())

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()

    def _registrar_intento(self, dto: LoginDTO, exitoso: bool, motivo_fallo: str | None) -> None:
        self.intentos.guardar(
            IntentoLogin(
                id=str(uuid4()),
                username=dto.username,
                fecha=datetime.utcnow(),
                ip=dto.ip,
                exitoso=exitoso,
                motivo_fallo=motivo_fallo,
            )
        )
