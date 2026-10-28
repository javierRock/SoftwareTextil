"""Traduccion centralizada de errores de Catalogo a HTTP."""

from rest_framework.exceptions import MethodNotAllowed, NotFound, ValidationError

from apps.catalogo.domain.excepciones import (
    OperacionNoPermitidaError,
    RecursoNoEncontradoError,
    ValidacionError,
)


class ManejoErroresCatalogoMixin:
    """Convierte errores de negocio sin acoplar dominio o aplicacion a DRF."""

    def handle_exception(self, exc):
        if isinstance(exc, ValidacionError):
            exc = ValidationError({"error": str(exc)})
        elif isinstance(exc, RecursoNoEncontradoError):
            exc = NotFound({"error": str(exc)})
        elif isinstance(exc, OperacionNoPermitidaError):
            exc = MethodNotAllowed(
                self.request.method,
                detail={"error": str(exc)},
            )
        return super().handle_exception(exc)
