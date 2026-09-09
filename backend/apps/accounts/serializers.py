from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import KYCProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "phone", "is_kyc_verified"]
        read_only_fields = ["id", "is_kyc_verified"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "phone"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class KYCProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = KYCProfile
        fields = [
            "id", "user", "business_name", "registration_number", "tax_id",
            "address", "status", "reviewed_by", "reviewed_at", "created_at",
        ]
        read_only_fields = ["status", "reviewed_by", "reviewed_at", "created_at"]


class KYCReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCProfile
        fields = ["status"]

    def validate_status(self, value):
        if value not in (KYCProfile.Status.APPROVED, KYCProfile.Status.REJECTED):
            raise serializers.ValidationError("Review status must be 'approved' or 'rejected'.")
        return value
