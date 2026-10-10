from rest_framework import serializers

from .models import LogisticsRequest, ShipmentUpdate


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    request = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ShipmentUpdate
        fields = ["id", "request", "status", "note", "timestamp"]
        read_only_fields = ["timestamp"]


class LogisticsRequestSerializer(serializers.ModelSerializer):
    updates = ShipmentUpdateSerializer(many=True, read_only=True)

    class Meta:
        model = LogisticsRequest
        fields = [
            "id", "order", "requested_by", "pickup_location", "delivery_location",
            "status", "assigned_partner", "created_at", "updates",
        ]
        read_only_fields = ["requested_by", "status", "created_at"]
