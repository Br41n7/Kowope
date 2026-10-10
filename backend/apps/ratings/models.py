from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Rating(models.Model):
    """A participant's review of another participant for one completed trade."""

    purchase_order = models.ForeignKey(
        "orders.PurchaseOrder", on_delete=models.CASCADE, related_name="ratings"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ratings_given"
    )
    reviewed = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ratings_received"
    )
    overall_score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    dimensions = models.JSONField(default=dict)
    comment = models.TextField(blank=True, max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["purchase_order", "reviewer", "reviewed"],
                name="unique_rating_per_trade_pair",
            ),
            models.CheckConstraint(
                condition=models.Q(overall_score__gte=1) & models.Q(overall_score__lte=5),
                name="rating_score_between_1_and_5",
            ),
        ]
        indexes = [models.Index(fields=["reviewed", "created_at"])]

    def __str__(self):
        return f"{self.purchase_order.po_number}: {self.reviewer} → {self.reviewed} ({self.overall_score}/5)"
