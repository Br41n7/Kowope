from django.contrib import admin

from .models import LogisticsRequest, ShipmentUpdate


@admin.register(LogisticsRequest)
class LogisticsRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "status", "assigned_partner", "created_at"]
    list_filter = ["status"]


@admin.register(ShipmentUpdate)
class ShipmentUpdateAdmin(admin.ModelAdmin):
    list_display = ["request", "status", "timestamp"]
