"""URLs DRF para pagos."""

from rest_framework.routers import DefaultRouter

from apps.ventas.pagos.presentation.views import PagoViewSet

router = DefaultRouter()
router.register(r"pagos", PagoViewSet, basename="pagos")

urlpatterns = router.urls
