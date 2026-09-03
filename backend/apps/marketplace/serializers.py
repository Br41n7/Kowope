from rest_framework import serializers

from .models import NegotiationMessage, Offer, RFQ


class RFQSerializer(serializers.ModelSerializer):
    buyer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RFQ
        fields = [
            "id", "buyer", "commodity", "grade", "quantity", "unit",
            "delivery_location", "delivery_date", "target_price",
            "quality_verification_pref", "payment_pref", "status", "created_at",
        ]
        read_only_fields = ["status", "created_at"]


class NegotiationMessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    offer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = NegotiationMessage
        fields = ["id", "offer", "sender", "message", "attachment", "created_at"]
        read_only_fields = ["created_at"]


class OfferSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    messages = NegotiationMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "rfq", "seller", "price", "delivery_period",
            "quality_certs", "status", "created_at", "messages",
        ]
        read_only_fields = ["status", "created_at"]

    def validate_rfq(self, rfq):
        if rfq.status != RFQ.Status.OPEN:
            raise serializers.ValidationError("This RFQ is no longer open for offers.")
        return rfq
