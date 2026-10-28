"""Excepciones del dominio de usuarios y autenticacion."""


class UsuariosError(Exception):
    """Error base para casos de uso de usuarios."""


class CredencialesInvalidasError(UsuariosError):
    """Se lanza cuando el usuario o la clave no coinciden."""


class UsuarioInactivoError(UsuariosError):
    """Se lanza cuando un usuario inactivo intenta iniciar sesion."""


class RecursoDuplicadoError(UsuariosError):
    """Se lanza cuando un campo unico ya fue registrado."""


class RecursoNoEncontradoError(UsuariosError):
    """Se lanza cuando una entidad requerida no existe."""


class OperacionNoPermitidaError(UsuariosError):
    """Se lanza cuando una regla de seguridad impide la operacion."""
