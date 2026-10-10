from rest_framework import serializers

from .models import InspectionPhoto, InspectionReport, InspectionRequest


class InspectionPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionPhoto
        fields = ["id", "image", "caption"]


class InspectionReportSerializer(serializers.ModelSerializer):
    photos = InspectionPhotoSerializer(many=True, required=False)
    request = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = InspectionReport
        fields = ["id", "request", "findings", "certificate_file", "gps_lat", "gps_lng", "submitted_at", "photos"]
        read_only_fields = ["submitted_at"]

    def create(self, validated_data):
        photos_data = validated_data.pop("photos", [])
        report = InspectionReport.objects.create(**validated_data)
        for photo_data in photos_data:
            InspectionPhoto.objects.create(report=report, **photo_data)
        return report


class InspectionRequestSerializer(serializers.ModelSerializer):
    report = InspectionReportSerializer(read_only=True)

    class Meta:
        model = InspectionRequest
        fields = ["id", "order", "requested_by", "status", "inspector", "created_at", "report"]
        read_only_fields = ["requested_by", "status", "created_at"]
