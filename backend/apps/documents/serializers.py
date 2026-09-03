from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    content_type = serializers.SlugRelatedField(slug_field="model", queryset=ContentType.objects.all())
    version = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = ["id", "owner", "content_type", "object_id", "doc_type", "file", "version", "uploaded_at"]
        read_only_fields = ["version", "uploaded_at"]
