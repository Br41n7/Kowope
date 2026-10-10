from rest_framework.routers import DefaultRouter

from .views import RatingViewSet

router = DefaultRouter(trailing_slash=False)
router.register("ratings", RatingViewSet, basename="rating")

urlpatterns = router.urls
