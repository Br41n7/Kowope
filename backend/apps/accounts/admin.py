from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import KYCProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "is_kyc_verified", "is_staff"]
    list_filter = ["role", "is_kyc_verified", "is_staff"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Trade Afric", {"fields": ("role", "phone", "is_kyc_verified")}),
    )


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = ["business_name", "user", "status", "reviewed_by", "created_at"]
    list_filter = ["status"]
    actions = ["approve_kyc", "reject_kyc"]

    @admin.action(description="Approve selected KYC profiles")
    def approve_kyc(self, request, queryset):
        for profile in queryset:
            profile.status = KYCProfile.Status.APPROVED
            profile.reviewed_by = request.user
            profile.save()
            profile.user.is_kyc_verified = True
            profile.user.save(update_fields=["is_kyc_verified"])

    @admin.action(description="Reject selected KYC profiles")
    def reject_kyc(self, request, queryset):
        queryset.update(status=KYCProfile.Status.REJECTED, reviewed_by=request.user)
