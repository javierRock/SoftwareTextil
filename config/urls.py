"""URL configuration del proyecto SoftwareTextil."""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
    # TODO: registrar routers de DRF cuando los views esten listos
    # path("api/", include("apps.usuarios.presentation.urls")),
    # path("api/", include("apps.catalogo.presentation.urls")),
    # path("api/", include("apps.inventario.presentation.urls")),
    # path("api/", include("apps.ventas.presentation.urls")),
]
