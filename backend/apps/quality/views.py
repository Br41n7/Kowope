from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import InspectionRequest
from .serializers import InspectionReportSerializer, InspectionRequestSerializer


class InspectionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = InspectionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = InspectionRequest.objects.all().select_related("order", "inspector", "report")

    @action(detail=True, methods=["post"], url_path="report")
    def submit_report(self, request, pk=None):
        inspection_request = self.get_object()
        serializer = InspectionReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save(request=inspection_request)
        inspection_request.status = InspectionRequest.Status.COMPLETED
        inspection_request.save(update_fields=["status"])
        return Response(InspectionReportSerializer(report).data, status=status.HTTP_201_CREATED)
