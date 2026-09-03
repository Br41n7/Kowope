from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsKYCVerified, IsOwnerOrReadOnly
from core.services.offer_service import accept_offer, reject_offer
from apps.orders.serializers import PurchaseOrderSerializer
from .models import NegotiationMessage, Offer, RFQ
from .serializers import NegotiationMessageSerializer, OfferSerializer, RFQSerializer


class RFQViewSet(viewsets.ModelViewSet):
    serializer_class = RFQSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCVerified, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "commodity"]
    owner_field = "buyer"

    def get_queryset(self):
        return RFQ.objects.all().select_related("buyer")

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)


class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated, IsKYCVerified]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "rfq"]
    owner_field = "seller"

    def get_permissions(self):
        # Editing/deleting an Offer is restricted to the seller who created it.
        # accept/reject/messages have their own actor checks (buyer-side actions),
        # handled inside the service layer / action bodies below.
        if self.action in ("update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsKYCVerified(), IsOwnerOrReadOnly()]
        return super().get_permissions()

    def get_queryset(self):
        return Offer.objects.all().select_related("rfq", "seller").prefetch_related("messages")

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        offer = self.get_object()
        order = accept_offer(offer, request.user)
        return Response(PurchaseOrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        offer = self.get_object()
        offer = reject_offer(offer, request.user)
        return Response(OfferSerializer(offer).data)

    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        offer = self.get_object()
        is_participant = request.user.id in (offer.seller_id, offer.rfq.buyer_id)
        if not is_participant:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the buyer or seller on this offer can message.")

        if request.method == "GET":
            qs = offer.messages.all()
            return Response(NegotiationMessageSerializer(qs, many=True).data)

        serializer = NegotiationMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(offer=offer, sender=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
