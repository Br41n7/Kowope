from rest_framework.routers import DefaultRouter

from .views import DocumentViewSet

router = DefaultRouter(trailing_slash=False)
router.register("documents", DocumentViewSet, basename="document")

urlpatterns = router.urls
