from django.contrib import admin

from .models import Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "purchase_order", "reviewer", "reviewed", "overall_score", "created_at")
    list_filter = ("overall_score", "created_at")
    search_fields = ("purchase_order__po_number", "reviewer__username", "reviewed__username", "comment")
    readonly_fields = ("created_at", "updated_at")
