"""Errores de aplicacion mapeables a respuestas HTTP."""


class AppError(Exception):
    status_code = 400
    code = "application_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status_code = 400
    code = "validation_error"


class AuthenticationError(AppError):
    status_code = 401
    code = "authentication_error"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class ExternalServiceError(AppError):
    status_code = 502
    code = "external_service_error"
