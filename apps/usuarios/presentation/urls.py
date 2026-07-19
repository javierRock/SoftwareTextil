"""URLs DRF para usuarios."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.usuarios.presentation.views import LoginView, LogoutView, RolViewSet, UsuarioViewSet

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")
router.register(r"roles", RolViewSet, basename="roles")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
]
urlpatterns += router.urls
