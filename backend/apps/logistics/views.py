from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LogisticsRequest, ShipmentUpdate
from .serializers import LogisticsRequestSerializer, ShipmentUpdateSerializer


class LogisticsRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LogisticsRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = LogisticsRequest.objects.all().select_related("order", "assigned_partner")

    @action(detail=True, methods=["post"], url_path="updates")
    def add_update(self, request, pk=None):
        logistics_request = self.get_object()
        serializer = ShipmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update = serializer.save(request=logistics_request)
        logistics_request.status = update.status
        logistics_request.save(update_fields=["status"])
        return Response(ShipmentUpdateSerializer(update).data, status=status.HTTP_201_CREATED)
