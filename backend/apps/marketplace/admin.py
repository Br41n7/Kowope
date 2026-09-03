from django.contrib import admin

from .models import NegotiationMessage, Offer, RFQ


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ["id", "commodity", "buyer", "quantity", "unit", "status", "created_at"]
    list_filter = ["status", "commodity"]


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ["id", "rfq", "seller", "price", "status", "created_at"]
    list_filter = ["status"]


@admin.register(NegotiationMessage)
class NegotiationMessageAdmin(admin.ModelAdmin):
    list_display = ["id", "offer", "sender", "created_at"]
