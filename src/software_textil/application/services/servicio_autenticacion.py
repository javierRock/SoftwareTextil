"""Casos de uso de autenticacion."""

from datetime import datetime, timedelta
from secrets import token_urlsafe
from uuid import uuid4

from software_textil.application.dtos.comandos import LoginDTO
from software_textil.application.ports import PasswordHasher
from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.compartido.enums import EstadoUsuario, ResultadoLogin
from software_textil.domain.usuarios.repositorios import RepositorioIntentoLogin, RepositorioSesion, RepositorioUsuario
from software_textil.domain.usuarios.usuario import IntentoLogin, Sesion


class ServicioAutenticacion:
    def __init__(
        self,
        usuarios: RepositorioUsuario,
        sesiones: RepositorioSesion,
        intentos: RepositorioIntentoLogin,
        password_hasher: PasswordHasher,
        unit_of_work: UnitOfWork | None = None,
    ) -> None:
        self.usuarios = usuarios
        self.sesiones = sesiones
        self.intentos = intentos
        self.password_hasher = password_hasher
        self.uow = unit_of_work or NoOpUnitOfWork()

    def autenticar(self, dto: LoginDTO) -> tuple[ResultadoLogin, Sesion | None]:
        usuario = self.usuarios.buscar_por_email(dto.username)
        if usuario is None or usuario.credencial is None:
            self._registrar_intento_fallido(dto, "usuario_no_encontrado")
            return ResultadoLogin.CREDENCIALES_INVALIDAS, None
        if usuario.estado != EstadoUsuario.ACTIVO:
            self._registrar_intento_fallido(dto, "usuario_inactivo")
            return ResultadoLogin.USUARIO_INACTIVO, None
        if not self.password_hasher.verify(dto.password, usuario.credencial.password_hash, usuario.credencial.salt):
            self._registrar_intento_fallido(dto, "password_incorrecto")
            return ResultadoLogin.CREDENCIALES_INVALIDAS, None

        with self.uow:
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
            self.uow.commit()
        return ResultadoLogin.EXITOSO, sesion

    def cerrar_sesion(self, token: str) -> None:
        sesion = self.sesiones.buscar_por_token(token)
        if sesion is not None:
            with self.uow:
                sesion.cerrar()
                self.sesiones.guardar(sesion)
                self.uow.commit()

    def validar_sesion(self, token: str) -> bool:
        sesion = self.sesiones.buscar_por_token(token)
        return bool(sesion and sesion.esta_activa())

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

    def _registrar_intento_fallido(self, dto: LoginDTO, motivo_fallo: str) -> None:
        with self.uow:
            self._registrar_intento(dto, False, motivo_fallo)
            self.uow.commit()
