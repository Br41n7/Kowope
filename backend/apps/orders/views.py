from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, viewsets
from django.db.models import Q

from .models import PurchaseOrder
from .serializers import PurchaseOrderSerializer

# Statuses a buyer or seller may move an order into via the API directly.
# (Anything beyond this — e.g. disputes — should go through a dedicated flow.)
ALLOWED_SELF_SERVICE_STATUSES = {
    PurchaseOrder.Status.IN_PROGRESS,
    PurchaseOrder.Status.DELIVERED,
    PurchaseOrder.Status.COMPLETED,
    PurchaseOrder.Status.DISPUTED,
}


class PurchaseOrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Orders are created only via Offer.accept() — never directly through this endpoint."""
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return PurchaseOrder.objects.none()
        user = self.request.user
        return PurchaseOrder.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related("buyer", "seller", "offer")

    def perform_update(self, serializer):
        new_status = self.request.data.get("status")
        if new_status and new_status not in ALLOWED_SELF_SERVICE_STATUSES:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Cannot set status to '{new_status}' via this endpoint.")
        serializer.save()
