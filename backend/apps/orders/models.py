import uuid

from django.conf import settings
from django.db import models


def generate_po_number():
    return f"PO-{uuid.uuid4().hex[:10].upper()}"


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        ISSUED = "issued", "Issued"
        IN_PROGRESS = "in_progress", "In progress"
        DELIVERED = "delivered", "Delivered"
        DISPUTED = "disputed", "Disputed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    offer = models.OneToOneField(
        "marketplace.Offer", on_delete=models.PROTECT, related_name="purchase_order"
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders_as_buyer"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders_as_seller"
    )
    po_number = models.CharField(max_length=30, unique=True, default=generate_po_number)
    terms_snapshot = models.JSONField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ISSUED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.po_number} [{self.status}]"


class OrderAmendment(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="amendments")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Amendment on {self.order.po_number}"
