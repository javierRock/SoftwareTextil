"""URLs DRF para pedidos."""

from rest_framework.routers import DefaultRouter

from apps.ventas.pedidos.presentation.views import PedidoViewSet

router = DefaultRouter()
router.register(r"pedidos", PedidoViewSet, basename="pedidos")

urlpatterns = router.urls
