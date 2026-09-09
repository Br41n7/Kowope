from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from core.mixins import RelativeMediaURLMixin
from .models import Document
from .serializers import DocumentSerializer


def _is_order_participant(user, related_object):
    """If the related object is a PurchaseOrder, only its buyer/seller/admin may touch its documents.
    Other content types (no buyer/seller attributes) fall back to authenticated-only access."""
    buyer_id = getattr(related_object, "buyer_id", None)
    seller_id = getattr(related_object, "seller_id", None)
    if buyer_id is None and seller_id is None:
        return True
    return user.role == "admin" or user.id in (buyer_id, seller_id)


class DocumentViewSet(RelativeMediaURLMixin, viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Document.objects.none()

        qs = Document.objects.all().select_related("content_type", "owner")
        content_type = self.request.query_params.get("content_type")
        object_id = self.request.query_params.get("object_id")
        if content_type:
            qs = qs.filter(content_type__model=content_type)
        if object_id:
            qs = qs.filter(object_id=object_id)

        user = self.request.user
        if user.role == "admin" or user.is_staff:
            return qs
        # Filter in Python since related_object varies by content type and we only expect
        # a handful of documents per order/RFQ — fine for MVP scale.
        allowed_ids = [doc.id for doc in qs if _is_order_participant(user, doc.related_object)]
        return qs.filter(id__in=allowed_ids)

    def perform_create(self, serializer):
        related_object = serializer.validated_data["content_type"].get_object_for_this_type(
            id=serializer.validated_data["object_id"]
        )
        if not _is_order_participant(self.request.user, related_object):
            raise PermissionDenied("You don't have access to attach documents to this record.")
        serializer.save(owner=self.request.user)
