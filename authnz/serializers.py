from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers

from authnz.models import User


class LoginEmailSerializer(serializers.Serializer):
    """
    Serializes data of login view.
    """

    email = serializers.EmailField(min_length=5, max_length=50)
    password = serializers.CharField(min_length=8, max_length=50)


class RegisterEmailSerializer(LoginEmailSerializer):
    """
    Serializes data of register view.
    """

    email = serializers.EmailField(min_length=5, max_length=50)
    password = serializers.CharField(min_length=8, max_length=50)

    def validate_password(self, password):
        try:
            # Validate password with django AUTH_PASSWORD_VALIDATORS
            validate_password(password)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return password


class MyProfileSerializer(serializers.Serializer):
    """
    Serializes user profile data.
    """

    email = serializers.ReadOnlyField()
    email_confirmed = serializers.ReadOnlyField()
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = User.objects.select_for_update().get(id=instance.id)
        update_fields = []
        if (
            validated_data.get("first_name")
            and instance.first_name != validated_data["first_name"]
        ):
            instance.first_name = validated_data["first_name"]
            update_fields.append("first_name")
        elif validated_data.get("first_name", None) is not None:  # blank
            instance.first_name = ""
            update_fields.append("first_name")
        if (
            validated_data.get("last_name")
            and instance.last_name != validated_data["last_name"]
        ):
            instance.last_name = validated_data["last_name"]
            update_fields.append("last_name")
        elif validated_data.get("last_name", None) is not None:  # blank
            instance.last_name = ""
            update_fields.append("last_name")

        instance.save(update_fields=update_fields)
        return instance


class NestedUserSerializer(serializers.Serializer):
    """
    Serializes user data in other instances.
    """

    email = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
