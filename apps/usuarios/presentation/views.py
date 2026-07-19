"""Views DRF para usuarios y autenticacion."""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.usuarios.application.services import ServicioAutenticacion, ServicioGestionUsuarios
from apps.usuarios.infrastructure.models import RolModel, UsuarioModel
from apps.usuarios.infrastructure.repositories import (
    DjangoRepositorioIntentoLogin,
    DjangoRepositorioRol,
    DjangoRepositorioSesion,
    DjangoRepositorioUsuario,
)
from apps.usuarios.presentation.serializers import (
    CrearUsuarioSerializer,
    LoginSerializer,
    RolSerializer,
    UsuarioSerializer,
)


def _servicio_auth() -> ServicioAutenticacion:
    return ServicioAutenticacion(
        DjangoRepositorioUsuario(),
        DjangoRepositorioSesion(),
        DjangoRepositorioIntentoLogin(),
    )


def _servicio_usuarios() -> ServicioGestionUsuarios:
    return ServicioGestionUsuarios(DjangoRepositorioUsuario(), DjangoRepositorioRol())


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio_auth()
        try:
            resultado = servicio.login(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
                ip=request.META.get("REMOTE_ADDR", ""),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(resultado, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        token = request.auth.key if request.auth else request.data.get("token", "")
        if not token:
            return Response({"error": "Token requerido"}, status=status.HTTP_400_BAD_REQUEST)
        servicio = _servicio_auth()
        servicio.logout(str(token))
        return Response({"mensaje": "Sesion cerrada"}, status=status.HTTP_200_OK)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = UsuarioModel.objects.all()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = CrearUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        servicio = _servicio_usuarios()
        try:
            usuario = servicio.crear_usuario(
                nombre=serializer.validated_data["nombre"],
                email=serializer.validated_data["email"],
                rol_id=serializer.validated_data["rol_id"],
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": usuario.id, "nombre": usuario.nombre, "email": usuario.email}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="desactivar")
    def desactivar(self, request, pk=None):
        servicio = _servicio_usuarios()
        try:
            servicio.desactivar_usuario(pk)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response({"mensaje": "Usuario desactivado"}, status=status.HTTP_200_OK)


class RolViewSet(viewsets.ModelViewSet):
    queryset = RolModel.objects.all()
    serializer_class = RolSerializer

    def create(self, request, *args, **kwargs):
        servicio = _servicio_usuarios()
        try:
            rol = servicio.crear_rol(
                nombre=request.data.get("nombre", ""),
                descripcion=request.data.get("descripcion", ""),
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(RolSerializer(rol).data, status=status.HTTP_201_CREATED)
