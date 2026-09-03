from rest_framework.routers import DefaultRouter

from .views import LogisticsRequestViewSet

router = DefaultRouter()
router.register("logistics-requests", LogisticsRequestViewSet, basename="logistics-request")

urlpatterns = router.urls
