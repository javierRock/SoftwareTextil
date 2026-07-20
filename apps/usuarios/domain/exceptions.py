"""Excepciones del dominio de usuarios y autenticacion."""


class ErrorUsuarios(Exception):
    """Error base para casos de uso de usuarios."""


class CredencialesInvalidas(ErrorUsuarios):
    """Se lanza cuando el usuario o la clave no coinciden."""


class UsuarioInactivo(ErrorUsuarios):
    """Se lanza cuando un usuario inactivo intenta iniciar sesion."""


class RecursoDuplicado(ErrorUsuarios):
    """Se lanza cuando un campo unico ya fue registrado."""


class RecursoNoEncontrado(ErrorUsuarios):
    """Se lanza cuando una entidad requerida no existe."""
