"""URL configuration del proyecto SoftwareTextil."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.usuarios.presentation.urls")),
    path("api/", include("apps.catalogo.presentation.urls")),
    path("api/", include("apps.inventario.presentation.urls")),
    path("api/ventas/", include("apps.ventas.carrito.presentation.urls")),
    path("api/ventas/", include("apps.ventas.pedidos.presentation.urls")),
    path("api/ventas/", include("apps.ventas.pagos.presentation.urls")),
]
