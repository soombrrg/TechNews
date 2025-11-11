from datetime import datetime

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.models import User
from main.models import Category, Post


class AuthorInfoSerializer(serializers.ModelSerializer):
    """Serializer for correct display of author info in OpenAPI."""

    class Meta:
        model = User
        fields = ["id", "username", "full_name", "avatar"]


class CategoryInfoSerializer(serializers.ModelSerializer):
    """Serializer for correct display of category info in OpenAPI."""

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class PostInfoSerializer(serializers.ModelSerializer):
    """Serializer for correct display of post info in OpenAPI."""

    class Meta:
        model = Post
        fields = ["id", "title", "slug", "content", "image", "views_count", "created"]


class PinnedPostDataSerializer(PostInfoSerializer):
    """Serializer for correct display of pinned post data in OpenAPI."""

    category = serializers.StringRelatedField(read_only=True)  # type: ignore[var-annotated]
    author = AuthorInfoSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    pinned_at = serializers.DateTimeField(read_only=True)

    class Meta(PostInfoSerializer.Meta):
        fields = PostInfoSerializer.Meta.fields + [
            "category",
            "author",
            "comments_count",
            "pinned_at",
            "is_pinned",
        ]


class PinnedPostsListSerializer(serializers.Serializer):
    """Serializer for correct display of pinned_posts_list view response data in OpenAPI."""

    count = serializers.IntegerField(read_only=True)
    results = PinnedPostDataSerializer(many=True, read_only=True)


class PinnedBySerializer(serializers.ModelSerializer):
    """Serializer for correct display of pinned by info in OpenAPI."""

    has_active_subscription = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "has_active_subscription"]

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_has_active_subscription(self, obj: User) -> bool:
        return obj.subscription.is_active if hasattr(obj, "subscription") else False


class PinInfoSerializer(serializers.ModelSerializer["Post"]):
    """Serializer for correct display of pin info in OpenAPI."""

    pinned_by = PinnedBySerializer(source="pin_info.user", read_only=True)
    pinned_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["pinned_by", "pinned_at"]

    @extend_schema_field(OpenApiTypes.DATETIME)
    def get_pinned_at(self, obj: Post) -> datetime | None:
        if hasattr(obj, "pin_info"):
            return obj.pin_info.pinned_at
        return None
