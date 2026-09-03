from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import IsAdminRole
from .models import KYCProfile
from .serializers import (
    KYCProfileSerializer,
    KYCReviewSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


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
