from rest_framework.routers import DefaultRouter

from .views import InspectionRequestViewSet

router = DefaultRouter()
router.register("inspection-requests", InspectionRequestViewSet, basename="inspection-request")

urlpatterns = router.urls
