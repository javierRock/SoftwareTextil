"""Permisos DRF para usuarios autenticados por sesion."""

from rest_framework.permissions import BasePermission


class EsAdministrador(BasePermission):
    """Permite el acceso a usuarios con rol de administrador."""

    def has_permission(self, request, _view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol.casefold() == "administrador"
        )


class EsCliente(BasePermission):
    """Permite el acceso a usuarios con rol de cliente."""

    def has_permission(self, request, _view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol.casefold() == "cliente"
        )
