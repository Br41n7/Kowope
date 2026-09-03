from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Document(models.Model):
    class DocType(models.TextChoices):
        PO = "po", "Purchase Order"
        INVOICE = "invoice", "Invoice"
        CERTIFICATE = "certificate", "Certificate"
        DELIVERY_NOTE = "delivery_note", "Delivery Note"
        OTHER = "other", "Other"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey("content_type", "object_id")

    doc_type = models.CharField(max_length=20, choices=DocType.choices, default=DocType.OTHER)
    file = models.FileField(upload_to="documents/%Y/%m/")
    version = models.PositiveIntegerField(default=1)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"{self.doc_type} v{self.version} for {self.content_type}#{self.object_id}"

    def save(self, *args, **kwargs):
        if not self.pk:
            latest = Document.objects.filter(
                content_type=self.content_type, object_id=self.object_id, doc_type=self.doc_type
            ).order_by("-version").first()
            self.version = (latest.version + 1) if latest else 1
        super().save(*args, **kwargs)
