from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        RFQ_OFFER = "rfq_offer", "New offer on RFQ"
        PO_ISSUED = "po_issued", "Purchase order issued"
        INSPECTION_DONE = "inspection_done", "Inspection completed"
        DISPUTE = "dispute", "Dispute raised"
        GENERAL = "general", "General"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=30, choices=Type.choices, default=Type.GENERAL)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.type}] {self.message[:40]}"
