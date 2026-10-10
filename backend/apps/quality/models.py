from django.conf import settings
from django.db import models


class InspectionRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"

    order = models.ForeignKey("orders.PurchaseOrder", on_delete=models.CASCADE, related_name="inspection_requests")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True,
        related_name="inspection_requests_made",
    )
    inspector = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="inspection_jobs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inspection for {self.order.po_number} [{self.status}]"


class InspectionReport(models.Model):
    request = models.OneToOneField(InspectionRequest, on_delete=models.CASCADE, related_name="report")
    findings = models.TextField()
    certificate_file = models.FileField(upload_to="inspection_certs/", blank=True, null=True)
    gps_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    gps_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.request}"


class InspectionPhoto(models.Model):
    report = models.ForeignKey(InspectionReport, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="inspection_photos/")
    caption = models.CharField(max_length=255, blank=True)
