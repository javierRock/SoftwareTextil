"""Contratos de persistencia para usuarios y autenticacion."""

from abc import ABC, abstractmethod

from apps.usuarios.domain.usuario import IntentoLogin, Rol, Sesion, Usuario


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

    @abstractmethod
    def buscar_por_username(self, username: str) -> Usuario | None:
        raise NotImplementedError

    @abstractmethod
    def set_password(self, usuario_id: str, password_hash: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_password(self, username: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[Usuario]:
        raise NotImplementedError


class RepositorioRol(ABC):
    @abstractmethod
    def guardar(self, rol: Rol) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, rol_id: str) -> Rol | None:
        raise NotImplementedError

    @abstractmethod
    def listar(self) -> list[Rol]:
        raise NotImplementedError


class RepositorioSesion(ABC):
    @abstractmethod
    def guardar(self, sesion: Sesion) -> None:
        raise NotImplementedError

    @abstractmethod
    def buscar_por_token(self, token: str) -> Sesion | None:
        raise NotImplementedError

    @abstractmethod
    def cerrar_por_token(self, token: str) -> None:
        raise NotImplementedError


class RepositorioIntentoLogin(ABC):
    @abstractmethod
    def guardar(self, intento: IntentoLogin) -> None:
        raise NotImplementedError
