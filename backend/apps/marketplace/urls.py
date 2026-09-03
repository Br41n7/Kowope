from rest_framework.routers import DefaultRouter

from .views import OfferViewSet, RFQViewSet

router = DefaultRouter()
router.register("rfqs", RFQViewSet, basename="rfq")
router.register("offers", OfferViewSet, basename="offer")

urlpatterns = router.urls
