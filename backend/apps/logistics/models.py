from django.conf import settings
from django.db import models


class LogisticsRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ASSIGNED = "assigned", "Assigned"
        IN_TRANSIT = "in_transit", "In transit"
        DELIVERED = "delivered", "Delivered"

    order = models.ForeignKey("orders.PurchaseOrder", on_delete=models.CASCADE, related_name="logistics_requests")
    pickup_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    assigned_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="logistics_jobs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Logistics for {self.order.po_number} [{self.status}]"


class ShipmentUpdate(models.Model):
    request = models.ForeignKey(LogisticsRequest, on_delete=models.CASCADE, related_name="updates")
    status = models.CharField(max_length=20, choices=LogisticsRequest.Status.choices)
    note = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.request_id} -> {self.status} @ {self.timestamp}"
