from rest_framework.exceptions import ValidationError

from apps.logistics.models import LogisticsRequest
from apps.orders.models import PurchaseOrder
from apps.quality.models import InspectionRequest


def ensure_rating_eligible(*, order, reviewer, reviewed):
    if order.status != PurchaseOrder.Status.COMPLETED:
        raise ValidationError({"purchase_order": "Ratings are available only after the purchase order is completed."})
    if reviewer.pk == reviewed.pk:
        raise ValidationError({"reviewed": "You cannot rate yourself."})

    # The two trade principals may rate one another.
    if reviewer.pk == order.buyer_id and reviewed.pk == order.seller_id:
        return reviewed.role
    if reviewer.pk == order.seller_id and reviewed.pk == order.buyer_id:
        return reviewed.role

    # MVP policy: only the person who requested a completed service may rate its provider.
    logistics_eligible = LogisticsRequest.objects.filter(
        order=order,
        requested_by=reviewer,
        assigned_partner=reviewed,
        status=LogisticsRequest.Status.DELIVERED,
    ).exists()
    if logistics_eligible and reviewed.role == "logistics":
        return reviewed.role

    inspection_eligible = InspectionRequest.objects.filter(
        order=order,
        requested_by=reviewer,
        inspector=reviewed,
        status=InspectionRequest.Status.COMPLETED,
    ).exists()
    if inspection_eligible and reviewed.role == "inspector":
        return reviewed.role

    raise ValidationError({
        "reviewed": "You can rate only the other trade participant, or a completed logistics/inspection provider for a service you requested on this purchase order."
    })
