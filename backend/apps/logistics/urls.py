from rest_framework.routers import DefaultRouter

from .views import LogisticsRequestViewSet

router = DefaultRouter(trailing_slash=False)
router.register("logistics-requests", LogisticsRequestViewSet, basename="logistics-request")

urlpatterns = router.urls
