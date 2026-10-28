"""Permisos DRF para usuarios autenticados por sesion."""

from rest_framework.permissions import BasePermission


def _tiene_rol(request, *roles: str) -> bool:
    usuario = getattr(request, "user", None)
    rol = getattr(usuario, "rol", "")
    return bool(
        usuario
        and getattr(usuario, "is_authenticated", False)
        and isinstance(rol, str)
        and rol.casefold() in {nombre.casefold() for nombre in roles}
    )


class EsAdministrador(BasePermission):
    """Permite el acceso a usuarios con rol de administrador."""

    def has_permission(self, request, _view) -> bool:
        return _tiene_rol(request, "Administrador")


class EsCliente(BasePermission):
    """Permite el acceso a usuarios con rol de cliente."""

    def has_permission(self, request, _view) -> bool:
        return _tiene_rol(request, "Cliente")


class EsPersonalInventario(BasePermission):
    """Permite operar el almacen a administradores y encargados."""

    def has_permission(self, request, _view) -> bool:
        return _tiene_rol(request, "Administrador", "Encargado de inventario")
