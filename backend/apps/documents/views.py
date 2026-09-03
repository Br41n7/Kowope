from rest_framework import permissions, viewsets

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Document.objects.all().select_related("content_type", "owner")
        content_type = self.request.query_params.get("content_type")
        object_id = self.request.query_params.get("object_id")
        if content_type:
            qs = qs.filter(content_type__model=content_type)
        if object_id:
            qs = qs.filter(object_id=object_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
