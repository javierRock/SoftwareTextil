"""Casos de uso para usuarios y roles."""

from uuid import uuid4

from software_textil.application.dtos.comandos import CrearUsuarioDTO
from software_textil.application.errors import NotFoundError
from software_textil.application.ports import PasswordHasher
from software_textil.application.unit_of_work import NoOpUnitOfWork, UnitOfWork
from software_textil.domain.usuarios.repositorios import RepositorioRol, RepositorioUsuario
from software_textil.domain.usuarios.usuario import Credencial, Rol, Usuario, UsuarioSistemaFabrica


class ServicioGestionUsuarios:
    def __init__(
        self,
        usuarios: RepositorioUsuario,
        roles: RepositorioRol,
        password_hasher: PasswordHasher | None = None,
        unit_of_work: UnitOfWork | None = None,
    ) -> None:
        self.usuarios = usuarios
        self.roles = roles
        self.password_hasher = password_hasher
        self.uow = unit_of_work or NoOpUnitOfWork()

    def crear_usuario(self, dto: CrearUsuarioDTO) -> Usuario:
        rol = self.roles.buscar_por_id(dto.rol_id)
        if rol is None:
            raise NotFoundError("El rol no existe")
        with self.uow:
            usuario = UsuarioSistemaFabrica.crear(dto.nombre, dto.email, rol, dto.creado_por)
            if dto.password:
                usuario.credencial = self._crear_credencial(dto.username or dto.email, dto.password)
            self.usuarios.guardar(usuario)
            self.uow.commit()
        return usuario

    def crear_rol(self, nombre: str, descripcion: str = "") -> Rol:
        with self.uow:
            rol = Rol(id=str(uuid4()), nombre=nombre, descripcion=descripcion)
            self.roles.guardar(rol)
            self.uow.commit()
        return rol

    def desactivar_usuario(self, usuario_id: str) -> Usuario:
        usuario = self._obtener_usuario(usuario_id)
        with self.uow:
            usuario.desactivar()
            self.usuarios.guardar(usuario)
            self.uow.commit()
        return usuario

    def asignar_rol(self, usuario_id: str, rol_id: str) -> Usuario:
        usuario = self._obtener_usuario(usuario_id)
        rol = self.roles.buscar_por_id(rol_id)
        if rol is None:
            raise NotFoundError("El rol no existe")
        with self.uow:
            usuario.asignar_rol(rol)
            self.usuarios.guardar(usuario)
            self.uow.commit()
        return usuario

    def asignar_credencial(self, usuario_id: str, password: str, username: str | None = None) -> Usuario:
        usuario = self._obtener_usuario(usuario_id)
        with self.uow:
            usuario.credencial = self._crear_credencial(username or usuario.email, password)
            self.usuarios.guardar(usuario)
            self.uow.commit()
        return usuario

    def _obtener_usuario(self, usuario_id: str) -> Usuario:
        usuario = self.usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise NotFoundError("El usuario no existe")
        return usuario

    def _crear_credencial(self, username: str, password: str) -> Credencial:
        if self.password_hasher is None:
            raise ValueError("No hay servicio de hashing configurado")
        return Credencial(
            username=username,
            password_hash=self.password_hasher.hash(password),
            salt="",
            algoritmo_hash=self.password_hasher.nombre,
        )
