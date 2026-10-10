from django.db.models import Q
from rest_framework import permissions, viewsets

from .models import Rating
from .serializers import RatingSerializer


class RatingViewSet(viewsets.ModelViewSet):
    """List ratings visible to the caller and create eligible trade ratings."""
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return Rating.objects.none()
        qs = Rating.objects.select_related("purchase_order", "reviewer", "reviewed")
        if user.role == "admin" or user.is_staff:
            return qs
        return qs.filter(Q(reviewer=user) | Q(reviewed=user) | Q(purchase_order__buyer=user) | Q(purchase_order__seller=user)).distinct()
