"""Endpoints REST para autenticacion, perfil y administracion de usuarios."""

from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.usuarios.application.services import (
    ServicioAutenticacion,
    ServicioGestionUsuarios,
)
from apps.usuarios.domain.exceptions import (
    CredencialesInvalidasError,
    RecursoDuplicadoError,
    RecursoNoEncontradoError,
    UsuariosError,
)
from apps.usuarios.infrastructure.models import RolModel, UsuarioModel
from apps.usuarios.infrastructure.repositories import (
    DjangoRepositorioIntentoLogin,
    DjangoRepositorioRol,
    DjangoRepositorioSesion,
    DjangoRepositorioUsuario,
)
from apps.usuarios.presentation.permissions import EsAdministrador
from apps.usuarios.presentation.serializers import (
    CambiarPasswordSerializer,
    CrearRolSerializer,
    CrearUsuarioSerializer,
    LoginSerializer,
    PerfilSerializer,
    RegistroSerializer,
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


def _respuesta_error(exc: Exception, codigo: int = status.HTTP_400_BAD_REQUEST):
    detalle = exc.messages if isinstance(exc, ValidationError) else str(exc)
    return Response({"error": detalle}, status=codigo)


def _token_actual(request) -> str:
    return str(getattr(request.auth, "token", ""))


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            resultado = _servicio_auth().login(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
                ip=request.META.get("REMOTE_ADDR", ""),
            )
        except CredencialesInvalidasError as exc:
            return _respuesta_error(exc, status.HTTP_401_UNAUTHORIZED)
        except UsuariosError as exc:
            return _respuesta_error(exc, status.HTTP_403_FORBIDDEN)
        return Response(resultado, status=status.HTTP_200_OK)


class RegistroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            usuario = _servicio_usuarios().registrar_cliente(
                **serializer.validated_data,
            )
        except RecursoDuplicadoError as exc:
            return _respuesta_error(exc, status.HTTP_409_CONFLICT)
        except (ValidationError, UsuariosError) as exc:
            return _respuesta_error(exc)
        return Response(
            {
                "id": usuario.id,
                "nombre": usuario.nombre,
                "email": usuario.email,
                "username": usuario.username,
                "rol": usuario.rol.nombre,
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _servicio_auth().logout(_token_actual(request))
        return Response({"mensaje": "Sesion cerrada"}, status=status.HTTP_200_OK)


class PerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = UsuarioModel.objects.select_related("rol").get(id=request.user.id)
        return Response(UsuarioSerializer(usuario).data)

    def patch(self, request):
        serializer = PerfilSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            _servicio_usuarios().actualizar_perfil(
                usuario_id=request.user.id,
                **serializer.validated_data,
            )
        except RecursoDuplicadoError as exc:
            return _respuesta_error(exc, status.HTTP_409_CONFLICT)
        except UsuariosError as exc:
            return _respuesta_error(exc)
        usuario = UsuarioModel.objects.select_related("rol").get(id=request.user.id)
        return Response(UsuarioSerializer(usuario).data)


class CambiarPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CambiarPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            _servicio_usuarios().cambiar_password(
                usuario_id=request.user.id,
                **serializer.validated_data,
            )
        except CredencialesInvalidasError as exc:
            return _respuesta_error(exc, status.HTTP_400_BAD_REQUEST)
        except (ValidationError, UsuariosError) as exc:
            return _respuesta_error(exc)
        _servicio_auth().cerrar_otras_sesiones(
            request.user.id,
            _token_actual(request),
        )
        return Response({"mensaje": "Contrasena actualizada"})


class CerrarOtrasSesionesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _servicio_auth().cerrar_otras_sesiones(
            request.user.id,
            _token_actual(request),
        )
        return Response({"mensaje": "Las otras sesiones fueron cerradas"})


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UsuarioModel.objects.select_related("rol").order_by("nombre")
    serializer_class = UsuarioSerializer
    permission_classes = [EsAdministrador]

    def create(self, request, *args, **kwargs):
        serializer = CrearUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            usuario = _servicio_usuarios().crear_usuario(
                creado_por=request.user.id,
                **serializer.validated_data,
            )
        except RecursoDuplicadoError as exc:
            return _respuesta_error(exc, status.HTTP_409_CONFLICT)
        except (ValidationError, UsuariosError) as exc:
            return _respuesta_error(exc)
        model = UsuarioModel.objects.select_related("rol").get(id=usuario.id)
        return Response(UsuarioSerializer(model).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def desactivar(self, request, pk=None):
        if str(request.user.id) == str(pk):
            return _respuesta_error(
                ValueError("No puedes desactivar tu propia cuenta"),
                status.HTTP_409_CONFLICT,
            )
        try:
            _servicio_usuarios().desactivar_usuario(pk)
            DjangoRepositorioSesion().cerrar_por_usuario(pk)
        except RecursoNoEncontradoError as exc:
            return _respuesta_error(exc, status.HTTP_404_NOT_FOUND)
        return Response({"mensaje": "Usuario desactivado"})

    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        try:
            _servicio_usuarios().activar_usuario(pk)
        except RecursoNoEncontradoError as exc:
            return _respuesta_error(exc, status.HTTP_404_NOT_FOUND)
        return Response({"mensaje": "Usuario activado"})


class RolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RolModel.objects.order_by("nombre")
    serializer_class = RolSerializer
    permission_classes = [EsAdministrador]

    def create(self, request, *args, **kwargs):
        serializer = CrearRolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rol = _servicio_usuarios().crear_rol(**serializer.validated_data)
        except RecursoDuplicadoError as exc:
            return _respuesta_error(exc, status.HTTP_409_CONFLICT)
        except UsuariosError as exc:
            return _respuesta_error(exc)
        model = RolModel.objects.get(id=rol.id)
        return Response(RolSerializer(model).data, status=status.HTTP_201_CREATED)
