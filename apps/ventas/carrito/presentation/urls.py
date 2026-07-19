"""URLs DRF para carrito de compras."""

from rest_framework.routers import DefaultRouter

from apps.ventas.carrito.presentation.views import CarritoViewSet

router = DefaultRouter()
router.register(r"carritos", CarritoViewSet, basename="carritos")

urlpatterns = router.urls
