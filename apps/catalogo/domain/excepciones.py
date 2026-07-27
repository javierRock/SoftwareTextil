"""Excepciones de negocio del modulo Catalogo."""


class CatalogoError(Exception):
    """Base para errores de negocio conocidos de Catalogo."""


class ValidacionError(CatalogoError):
    """Los datos no cumplen una regla del dominio o del caso de uso."""


class RecursoNoEncontradoError(CatalogoError):
    """Un recurso requerido por el caso de uso no existe."""


class OperacionNoPermitidaError(CatalogoError):
    """La operacion solicitada no esta permitida por las reglas del negocio."""
