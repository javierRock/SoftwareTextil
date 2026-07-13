"""URLs DRF para catalogo."""

from rest_framework.routers import DefaultRouter

from apps.catalogo.presentation.views import CategoriaViewSet, PrendaViewSet, TipoProductoViewSet

router = DefaultRouter()
router.register(r"prendas", PrendaViewSet, basename="prendas")
router.register(r"categorias", CategoriaViewSet, basename="categorias")
router.register(r"tipos-producto", TipoProductoViewSet, basename="tipos-producto")

urlpatterns = router.urls
