"""Autenticacion DRF basada en sesiones del modulo usuarios."""

from dataclasses import dataclass

from django.utils import timezone
from rest_framework import authentication, exceptions

from apps.usuarios.infrastructure.models import SesionModel, UsuarioModel

CANTIDAD_PARTES_TOKEN = 2


@dataclass(frozen=True)
class UsuarioAutenticado:
    """Representa al usuario autenticado sin acoplarlo al modelo auth de Django."""

    id: str
    nombre: str
    username: str
    email: str
    rol: str
    is_authenticated: bool = True


class SesionTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        token = self._obtener_token(request)
        if not token:
            return None

        sesion = (
            SesionModel.objects.select_related("usuario", "usuario__rol")
            .filter(token=token, estado="activa")
            .first()
        )
        if (
            sesion is None
            or not sesion.fecha_expiracion
            or sesion.fecha_expiracion <= timezone.now()
        ):
            return self._validar_sesion_expirada(sesion)

        if sesion.usuario.estado != "activo":
            raise exceptions.AuthenticationFailed("El usuario esta inactivo")

        usuario = self._crear_usuario_autenticado(sesion.usuario)
        return (usuario, sesion)

    def authenticate_header(self, _request) -> str:
        return self.keyword

    def _obtener_token(self, request) -> str:
        auth = authentication.get_authorization_header(request).decode("utf-8").split()
        if len(auth) == CANTIDAD_PARTES_TOKEN and auth[0] in {self.keyword, "Token"}:
            return auth[1].strip()
        return ""

    def _validar_sesion_expirada(self, sesion):
        if sesion is None:
            raise exceptions.AuthenticationFailed("Token de sesion invalido")

        if not sesion.fecha_expiracion or sesion.fecha_expiracion <= timezone.now():
            sesion.estado = "expirada"
            sesion.save(update_fields=["estado"])
            raise exceptions.AuthenticationFailed("Token de sesion expirado")
        raise exceptions.AuthenticationFailed("Token de sesion invalido")

    def _crear_usuario_autenticado(self, usuario: UsuarioModel) -> UsuarioAutenticado:
        return UsuarioAutenticado(
            id=str(usuario.id),
            nombre=usuario.nombre,
            username=usuario.username,
            email=usuario.email,
            rol=usuario.rol.nombre,
        )
