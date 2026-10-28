"""URLs DRF para despachos."""

from rest_framework.routers import DefaultRouter

from apps.ventas.despachos.presentation.views import DespachoViewSet

router = DefaultRouter()
router.register(r"despachos", DespachoViewSet, basename="despachos")

urlpatterns = router.urls
