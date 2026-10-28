"""URLs DRF para inventario."""

from rest_framework.routers import DefaultRouter

from apps.inventario.presentation.views import MovimientoViewSet, StockViewSet

router = DefaultRouter()
router.register(r"stock", StockViewSet, basename="stock")
router.register(r"movimientos", MovimientoViewSet, basename="movimientos")

urlpatterns = router.urls
