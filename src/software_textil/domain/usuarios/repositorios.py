"""Contratos de persistencia para usuarios y autenticacion."""

from abc import ABC, abstractmethod

from software_textil.domain.usuarios.usuario import IntentoLogin, Rol, Sesion, Usuario


class RepositorioUsuario(ABC):
    @abstractmethod
    def guardar(self, usuario: Usuario) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, usuario_id: str) -> Usuario | None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_email(self, email: str) -> Usuario | None:
        raise NotImplementedError


class RepositorioRol(ABC):
    @abstractmethod
    def guardar(self, rol: Rol) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, rol_id: str) -> Rol | None:
        raise NotImplementedError


class RepositorioSesion(ABC):
    @abstractmethod
    def guardar(self, sesion: Sesion) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_token(self, token: str) -> Sesion | None:
        raise NotImplementedError


class RepositorioIntentoLogin(ABC):
    @abstractmethod
    def guardar(self, intento: IntentoLogin) -> None:
        raise NotImplementedError
