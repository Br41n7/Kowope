from django.contrib import admin

from .models import OrderAmendment, PurchaseOrder


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["po_number", "buyer", "seller", "status", "created_at"]
    list_filter = ["status"]
    readonly_fields = ["terms_snapshot", "po_number"]


@admin.register(OrderAmendment)
class OrderAmendmentAdmin(admin.ModelAdmin):
    list_display = ["order", "requested_by", "created_at"]
