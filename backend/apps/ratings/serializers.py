from rest_framework import serializers

from apps.orders.models import PurchaseOrder
from .criteria import validate_dimensions
from .eligibility import ensure_rating_eligible
from .models import Rating


class RatingSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Rating
        fields = [
            "id", "purchase_order", "reviewer", "reviewed", "overall_score",
            "dimensions", "comment", "created_at", "updated_at",
        ]
        read_only_fields = ["reviewer", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        order = attrs.get("purchase_order")
        reviewed = attrs.get("reviewed")
        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication is required.")
        if order is None or reviewed is None:
            return attrs
        role = ensure_rating_eligible(order=order, reviewer=request.user, reviewed=reviewed)
        if Rating.objects.filter(
            purchase_order=order, reviewer=request.user, reviewed=reviewed
        ).exists():
            raise serializers.ValidationError({
                "reviewed": "You have already rated this participant for this purchase order."
            })
        error = validate_dimensions(role, attrs.get("dimensions", {}))
        if error:
            raise serializers.ValidationError({"dimensions": error})
        return attrs

    def create(self, validated_data):
        return Rating.objects.create(reviewer=self.context["request"].user, **validated_data)
