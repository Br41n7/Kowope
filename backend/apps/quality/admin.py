from django.contrib import admin

from .models import InspectionPhoto, InspectionReport, InspectionRequest


@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "status", "inspector", "created_at"]
    list_filter = ["status"]


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = ["request", "submitted_at"]


admin.site.register(InspectionPhoto)
