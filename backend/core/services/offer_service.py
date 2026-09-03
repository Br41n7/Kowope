"""
Business logic for the offer -> purchase order lifecycle.
Kept out of views/serializers so it's reusable from admin actions,
Celery tasks, and tests without duplication.
"""
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError


def accept_offer(offer, actor):
    """
    Accept an Offer on behalf of the RFQ's buyer.
    - Validates the actor is the RFQ's buyer.
    - Marks the RFQ closed and the Offer accepted.
    - Creates a PurchaseOrder with an immutable terms_snapshot.
    Returns the created PurchaseOrder.
    """
    from apps.orders.models import PurchaseOrder  # local import avoids circular import

    rfq = offer.rfq

    if rfq.buyer_id != actor.id:
        raise PermissionDenied("Only the RFQ's buyer can accept an offer.")

    if rfq.status != rfq.Status.OPEN:
        raise ValidationError("This RFQ is not open — it may already be closed or cancelled.")

    if offer.status != offer.Status.SUBMITTED and offer.status != offer.Status.COUNTERED:
        raise ValidationError(f"Offer cannot be accepted from status '{offer.status}'.")

    with transaction.atomic():
        offer.status = offer.Status.ACCEPTED
        offer.save(update_fields=["status"])

        rfq.status = rfq.Status.CLOSED
        rfq.save(update_fields=["status"])

        # Reject all other offers on this RFQ
        rfq.offers.exclude(pk=offer.pk).update(status=offer.Status.REJECTED)

        terms_snapshot = {
            "commodity": rfq.commodity,
            "grade": rfq.grade,
            "quantity": str(rfq.quantity),
            "unit": rfq.unit,
            "delivery_location": rfq.delivery_location,
            "delivery_date": str(rfq.delivery_date),
            "price": str(offer.price),
            "delivery_period": offer.delivery_period,
            "quality_verification_pref": rfq.quality_verification_pref,
            "payment_pref": rfq.payment_pref,
        }

        order = PurchaseOrder.objects.create(
            offer=offer,
            buyer=rfq.buyer,
            seller=offer.seller,
            terms_snapshot=terms_snapshot,
        )

    from core.services.notification_service import notify
    notify(offer.seller, "po_issued", f"Your offer on RFQ #{rfq.id} was accepted — {order.po_number} issued.")
    notify(rfq.buyer, "po_issued", f"Purchase order {order.po_number} created for RFQ #{rfq.id}.")

    return order


def reject_offer(offer, actor):
    rfq = offer.rfq
    if rfq.buyer_id != actor.id:
        raise PermissionDenied("Only the RFQ's buyer can reject an offer.")
    offer.status = offer.Status.REJECTED
    offer.save(update_fields=["status"])
    return offer
