from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "doc_type", "content_type", "object_id", "version", "owner", "uploaded_at"]
    list_filter = ["doc_type"]
