"""URLs DRF para usuarios."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.usuarios.presentation.views import (
    CambiarPasswordView,
    CerrarOtrasSesionesView,
    LoginView,
    LogoutView,
    PerfilView,
    RegistroView,
    RolViewSet,
    UsuarioViewSet,
)

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")
router.register(r"roles", RolViewSet, basename="roles")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/registro/", RegistroView.as_view(), name="registro"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/perfil/", PerfilView.as_view(), name="perfil"),
    path(
        "auth/cambiar-password/",
        CambiarPasswordView.as_view(),
        name="cambiar-password",
    ),
    path(
        "auth/cerrar-otras-sesiones/",
        CerrarOtrasSesionesView.as_view(),
        name="cerrar-otras-sesiones",
    ),
]
urlpatterns += router.urls
