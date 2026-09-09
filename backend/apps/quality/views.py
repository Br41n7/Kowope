from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from core.mixins import RelativeMediaURLMixin
from core.permissions import IsInspectorRole
from .models import InspectionRequest
from .serializers import InspectionReportSerializer, InspectionRequestSerializer


class InspectionRequestViewSet(RelativeMediaURLMixin, viewsets.ModelViewSet):
    serializer_class = InspectionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = InspectionRequest.objects.all().select_related("order", "inspector", "report")
        if getattr(self, "swagger_fake_view", False) or not user.is_authenticated:
            return base.none()
        if user.role == "admin" or user.is_staff:
            return base
        if user.role == "inspector":
            return base.filter(Q(status=InspectionRequest.Status.REQUESTED) | Q(inspector=user))
        return base.filter(Q(order__buyer=user) | Q(order__seller=user))

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        user = self.request.user
        if user.id not in (order.buyer_id, order.seller_id) and user.role != "admin":
            raise PermissionDenied("Only the order's buyer or seller can request an inspection for it.")
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsInspectorRole])
    def assign(self, request, pk=None):
        """An inspector claims an unassigned request from the job pool."""
        inspection_request = self.get_object()
        if inspection_request.inspector_id is not None:
            raise ValidationError("This inspection has already been assigned.")
        inspection_request.inspector = request.user
        inspection_request.status = InspectionRequest.Status.SCHEDULED
        inspection_request.save(update_fields=["inspector", "status"])
        return Response(InspectionRequestSerializer(inspection_request).data)

    @action(detail=True, methods=["post"], url_path="report")
    def submit_report(self, request, pk=None):
        inspection_request = self.get_object()
        user = request.user
        is_assigned_inspector = inspection_request.inspector_id == user.id
        if not (is_assigned_inspector or user.role == "admin" or user.is_staff):
            raise PermissionDenied("Only the assigned inspector can submit this report.")

        serializer = InspectionReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save(request=inspection_request)
        inspection_request.status = InspectionRequest.Status.COMPLETED
        inspection_request.save(update_fields=["status"])
        return Response(InspectionReportSerializer(report).data, status=status.HTTP_201_CREATED)
