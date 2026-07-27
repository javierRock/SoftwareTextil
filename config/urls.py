"""URL configuration del proyecto SoftwareTextil."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.usuarios.presentation.urls")),
    path("api/", include("apps.catalogo.presentation.urls")),
    path("api/", include("apps.inventario.presentation.urls")),
    path("api/ventas/", include("apps.ventas.carrito.presentation.urls")),
    path("api/ventas/", include("apps.ventas.pedidos.presentation.urls")),
    path("api/ventas/", include("apps.ventas.pagos.presentation.urls")),
    path("api/ventas/", include("apps.ventas.despachos.presentation.urls")),
    # BrowserRouter necesita que cada ruta visual entregue el mismo index.
    # Las rutas de API y Django se resuelven antes de este fallback.
    re_path(
        r"^(?!api/|admin/|static/|media/).*$",
        TemplateView.as_view(template_name="index.html"),
        name="spa",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
