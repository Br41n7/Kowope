from django.conf import settings
from django.db import models


class RFQ(models.Model):
    class QualityPref(models.TextChoices):
        DELIVERY_TEST = "delivery_test", "Test on delivery"
        INDEPENDENT = "independent", "Independent verification"
        SAMPLE = "sample", "Sample testing"

    class PaymentPref(models.TextChoices):
        ESCROW = "escrow", "Escrow"
        GUARANTEE = "guarantee", "Bank guarantee"
        CREDIT = "credit", "Credit sale"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        CANCELLED = "cancelled", "Cancelled"

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rfqs")
    commodity = models.CharField(max_length=255)
    grade = models.CharField(max_length=100, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    unit = models.CharField(max_length=20, default="MT")
    delivery_location = models.CharField(max_length=255)
    delivery_date = models.DateField()
    target_price = models.DecimalField(max_digits=14, decimal_places=2)
    quality_verification_pref = models.CharField(max_length=20, choices=QualityPref.choices)
    payment_pref = models.CharField(max_length=20, choices=PaymentPref.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"RFQ #{self.pk}: {self.commodity} ({self.quantity}{self.unit})"


class Offer(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        COUNTERED = "countered", "Countered"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="offers")
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="offers")
    price = models.DecimalField(max_digits=14, decimal_places=2)
    delivery_period = models.CharField(max_length=100)
    quality_certs = models.FileField(upload_to="offer_certs/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("rfq", "seller")

    def __str__(self):
        return f"Offer #{self.pk} on RFQ #{self.rfq_id} by {self.seller}"


class NegotiationMessage(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    attachment = models.FileField(upload_to="negotiation_attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message on Offer #{self.offer_id} by {self.sender}"
