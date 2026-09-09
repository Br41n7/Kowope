from rest_framework.routers import DefaultRouter

from .views import InspectionRequestViewSet

router = DefaultRouter(trailing_slash=False)
router.register("inspection-requests", InspectionRequestViewSet, basename="inspection-request")

urlpatterns = router.urls
