from rest_framework import serializers

from .models import OrderAmendment, PurchaseOrder


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = [
            "id", "offer", "buyer", "seller", "po_number",
            "terms_snapshot", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["offer", "buyer", "seller", "po_number", "terms_snapshot", "created_at", "updated_at"]


class OrderAmendmentSerializer(serializers.ModelSerializer):
    requested_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = OrderAmendment
        fields = ["id", "order", "requested_by", "description", "created_at"]
        read_only_fields = ["created_at"]
