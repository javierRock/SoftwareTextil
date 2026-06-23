"""Casos de uso para usuarios y roles."""

from software_textil.application.dtos.comandos import CrearUsuarioDTO
from software_textil.domain.usuarios.repositorios import RepositorioRol, RepositorioUsuario
from uuid import uuid4

from software_textil.domain.usuarios.usuario import Rol, Usuario, UsuarioSistemaFabrica


class ServicioGestionUsuarios:
    def __init__(self, usuarios: RepositorioUsuario, roles: RepositorioRol) -> None:
        self.usuarios = usuarios
        self.roles = roles

    def crear_usuario(self, dto: CrearUsuarioDTO) -> Usuario:
        rol = self.roles.buscar_por_id(dto.rol_id)
        if rol is None:
            raise ValueError("El rol no existe")
        usuario = UsuarioSistemaFabrica.crear(dto.nombre, dto.email, rol, dto.creado_por)
        self.usuarios.guardar(usuario)
        return usuario

    def crear_rol(self, nombre: str, descripcion: str = "") -> Rol:
        rol = Rol(id=str(uuid4()), nombre=nombre, descripcion=descripcion)
        self.roles.guardar(rol)
        return rol

    def desactivar_usuario(self, usuario_id: str) -> Usuario:
        usuario = self._obtener_usuario(usuario_id)
        usuario.desactivar()
        self.usuarios.guardar(usuario)
        return usuario

    def asignar_rol(self, usuario_id: str, rol_id: str) -> Usuario:
        usuario = self._obtener_usuario(usuario_id)
        rol = self.roles.buscar_por_id(rol_id)
        if rol is None:
            raise ValueError("El rol no existe")
        usuario.asignar_rol(rol)
        self.usuarios.guardar(usuario)
        return usuario

    def _obtener_usuario(self, usuario_id: str) -> Usuario:
        usuario = self.usuarios.buscar_por_id(usuario_id)
        if usuario is None:
            raise ValueError("El usuario no existe")
        return usuario
