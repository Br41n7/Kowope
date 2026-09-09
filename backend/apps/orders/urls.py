from rest_framework.routers import DefaultRouter

from .views import PurchaseOrderViewSet

router = DefaultRouter(trailing_slash=False)
router.register("orders", PurchaseOrderViewSet, basename="order")

urlpatterns = router.urls
