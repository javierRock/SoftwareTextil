"""URL configuration del proyecto SoftwareTextil."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="inicio"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.usuarios.presentation.urls")),
    path("api/", include("apps.catalogo.presentation.urls")),
    path("api/", include("apps.inventario.presentation.urls")),
    path("api/ventas/", include("apps.ventas.carrito.presentation.urls")),
    path("api/ventas/", include("apps.ventas.pedidos.presentation.urls")),
    path("api/ventas/", include("apps.ventas.pagos.presentation.urls")),
    path("api/ventas/", include("apps.ventas.despachos.presentation.urls")),
]
