from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import IsAdminRole
from .models import KYCProfile
from .serializers import (
    KYCProfileSerializer,
    KYCReviewSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


def _cookie_kwargs():
    return dict(
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path="/",
    )


def _set_auth_cookies(response, access, refresh):
    response.set_cookie(settings.AUTH_COOKIE_ACCESS, str(access), **_cookie_kwargs())
    response.set_cookie(settings.AUTH_COOKIE_REFRESH, str(refresh), **_cookie_kwargs())


def _clear_auth_cookies(response):
    response.delete_cookie(settings.AUTH_COOKIE_ACCESS, path="/")
    response.delete_cookie(settings.AUTH_COOKIE_REFRESH, path="/")


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response = Response({"user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        _set_auth_cookies(response, refresh.access_token, refresh)
        return response


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        response = Response({"user": UserSerializer(user).data})
        _set_auth_cookies(response, refresh.access_token, refresh)
        return response


class RefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        raw_refresh = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if not raw_refresh:
            return Response({"detail": "No refresh cookie present."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(raw_refresh)
        except TokenError:
            response = Response({"detail": "Refresh token invalid or expired."}, status=status.HTTP_401_UNAUTHORIZED)
            _clear_auth_cookies(response)
            return response

        response = Response({"detail": "refreshed"})
        response.set_cookie(settings.AUTH_COOKIE_ACCESS, str(refresh.access_token), **_cookie_kwargs())
        return response


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        response = Response({"detail": "logged out"})
        _clear_auth_cookies(response)
        return response


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class KYCSubmitView(generics.CreateAPIView):
    """Buyer/Seller submits (or resubmits) their KYC profile."""
    serializer_class = KYCProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        profile, _ = KYCProfile.objects.update_or_create(
            user=request.user,
            defaults={
                "business_name": request.data.get("business_name", ""),
                "registration_number": request.data.get("registration_number", ""),
                "tax_id": request.data.get("tax_id", ""),
                "address": request.data.get("address", ""),
                "status": KYCProfile.Status.PENDING,
            },
        )
        return Response(KYCProfileSerializer(profile).data, status=status.HTTP_201_CREATED)


class KYCReviewViewSet(viewsets.ModelViewSet):
    """Admin-only: list pending KYC submissions and approve/reject them."""
    queryset = KYCProfile.objects.select_related("user").all().order_by("-created_at")
    serializer_class = KYCProfileSerializer
    permission_classes = [IsAdminRole]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        review_serializer = KYCReviewSerializer(instance, data=request.data, partial=True)
        review_serializer.is_valid(raise_exception=True)
        review_serializer.save(reviewed_by=request.user, reviewed_at=timezone.now())

        if instance.status == KYCProfile.Status.APPROVED:
            instance.user.is_kyc_verified = True
            instance.user.save(update_fields=["is_kyc_verified"])
        elif instance.status == KYCProfile.Status.REJECTED:
            instance.user.is_kyc_verified = False
            instance.user.save(update_fields=["is_kyc_verified"])

        return Response(KYCProfileSerializer(instance).data)
