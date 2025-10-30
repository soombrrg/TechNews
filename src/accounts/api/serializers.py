from typing import Any

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.models import User


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for correct refresh token display in OpenAPI."""

    refresh_token = serializers.CharField(read_only=True)


class UserRegistrationSerializer(serializers.ModelSerializer[User]):
    """Serializer for registering new users"""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password_confirmation",
            "first_name",
            "last_name",
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError(
                {"password": "Password fields does not match."},
            )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        validated_data.pop("password_confirmation")
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user logging in"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any] | None:
        email = attrs.get("email")
        password = attrs.get("password")
        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                username=email,
                password=password,
            )
            if not user:
                raise serializers.ValidationError("User not found.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')


class UserProfileSerializer(serializers.ModelSerializer[User]):
    """Serializer for user profile"""

    full_name = serializers.ReadOnlyField()
    posts_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "bio",
            "posts_count",
            "comments_count",
            "created",
            "modified",
        )
        read_only_fields = ("id", "created", "modified")

    @extend_schema_field(OpenApiTypes.INT)
    def get_posts_count(self, obj: User) -> int:
        try:
            return obj.posts.count()
        except AttributeError:
            return 0

    @extend_schema_field(OpenApiTypes.INT)
    def get_comments_count(self, obj: User) -> int:
        try:
            return obj.comments.count()
        except AttributeError:
            return 0


class UserUpdateSerializer(serializers.ModelSerializer[User]):
    """Serializer for updating user profile"""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "avatar",
            "bio",
        )

    def update(self, instance: User, validated_data: dict) -> User:
        for attrs, value in validated_data.items():
            setattr(instance, attrs, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirmation = serializers.CharField(required=True)

    def validate_old_password(self, value: str) -> str | None:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["new_password"] != attrs["new_password_confirmation"]:
            raise serializers.ValidationError(
                {"new_password": "Password fields does not match."}
            )
        return attrs

    def save(self, **kwargs: Any) -> User:
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
