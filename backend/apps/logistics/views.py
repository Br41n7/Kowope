from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.permissions import IsLogisticsRole
from .models import LogisticsRequest, ShipmentUpdate
from .serializers import LogisticsRequestSerializer, ShipmentUpdateSerializer


class LogisticsRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LogisticsRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = LogisticsRequest.objects.all().select_related("order", "assigned_partner")
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return base.none()
        if user.role == "admin" or user.is_staff:
            return base
        if user.role == "logistics":
            # Logistics partners see the open job pool plus jobs already assigned to them.
            return base.filter(Q(status=LogisticsRequest.Status.REQUESTED) | Q(assigned_partner=user))
        # Buyers/sellers see logistics requests on their own orders only.
        return base.filter(Q(order__buyer=user) | Q(order__seller=user))

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        user = self.request.user
        if user.id not in (order.buyer_id, order.seller_id) and user.role != "admin":
            raise PermissionDenied("Only the order's buyer or seller can request logistics for it.")
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsLogisticsRole])
    def assign(self, request, pk=None):
        """A logistics partner claims an unassigned request from the job pool."""
        logistics_request = self.get_object()
        if logistics_request.assigned_partner_id is not None:
            raise ValidationError("This request has already been assigned.")
        logistics_request.assigned_partner = request.user
        logistics_request.status = LogisticsRequest.Status.ASSIGNED
        logistics_request.save(update_fields=["assigned_partner", "status"])
        return Response(LogisticsRequestSerializer(logistics_request).data)

    @action(detail=True, methods=["post"], url_path="updates")
    def add_update(self, request, pk=None):
        logistics_request = self.get_object()
        user = request.user
        is_assigned_partner = logistics_request.assigned_partner_id == user.id
        if not (is_assigned_partner or user.role == "admin" or user.is_staff):
            raise PermissionDenied("Only the assigned logistics partner can update this shipment.")

        serializer = ShipmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update = serializer.save(request=logistics_request)
        logistics_request.status = update.status
        logistics_request.save(update_fields=["status"])
        return Response(ShipmentUpdateSerializer(update).data, status=status.HTTP_201_CREATED)
