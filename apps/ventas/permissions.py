"""Permisos propios del contexto de ventas."""

from rest_framework.permissions import BasePermission


class EsEncargadoInventario(BasePermission):
    def has_permission(self, request, _view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol.casefold() == "encargado de inventario"
        )
