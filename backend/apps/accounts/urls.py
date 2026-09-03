from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import KYCReviewViewSet, KYCSubmitView, MeView, RegisterView

router = DefaultRouter()
router.register("kyc-review", KYCReviewViewSet, basename="kyc-review")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("kyc/submit/", KYCSubmitView.as_view(), name="kyc-submit"),
] + router.urls
