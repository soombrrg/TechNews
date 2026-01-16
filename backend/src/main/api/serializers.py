from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from app.serializer import (
    AuthorInfoSerializer,
    CategoryInfoSerializer,
    PinnedBySerializer,
)
from main.models import Category, Post
from subscribe.models import PinnedPost


class PinInfoSerializer(serializers.ModelSerializer["PinnedPost"]):
    """Serializer for correct display of pin info in OpenAPI."""

    pinned_by = PinnedBySerializer(source="user", read_only=True)

    class Meta:
        model = PinnedPost
        fields = ["pinned_by", "pinned_at"]


class CategorySerializer(serializers.ModelSerializer[Category]):
    """Serializer for Category"""

    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "created",
            "posts_count",
        ]
        read_only_fields = ["slug", "created"]


class PostBaseSerializer(serializers.ModelSerializer[Post]):

    comments_count = serializers.IntegerField(read_only=True)
    is_pinned = serializers.ReadOnlyField()
    pinned_info = PinInfoSerializer(source="pin_info", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "image",
            "author",
            "category",
            "publication_status",
            "comments_count",
            "views_count",
            "is_pinned",
            "pinned_info",
            "created",
            "modified",
        ]
        read_only_fields = ["slug", "author", "views_count"]

    @extend_schema_field(PinInfoSerializer)
    def get_pinned_info(self, obj: Post) -> dict[str, Any] | None:
        """Returns pin info if post is pinned"""
        if obj.is_pinned:
            return PinInfoSerializer(obj.pin_info).data
        return None


class PostListSerializer(PostBaseSerializer):
    """Serializer for list of Posts"""

    author = serializers.StringRelatedField()  # type: ignore[var-annotated]
    category = serializers.StringRelatedField()  # type: ignore[var-annotated]

    def create(self, validated_data: dict[str, Any]) -> Post:
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def to_representation(self, instance: Post) -> dict[str, Any]:
        data = super().to_representation(instance)
        # For Posts cards better viewing
        if len(data["content"]) > 200:
            data["content"] = data["content"][:200] + "..."
        return data


class PostDetailSerializer(PostBaseSerializer):
    """Serializer for Post details"""

    author_info = AuthorInfoSerializer(source="author", read_only=True)
    category_info = CategoryInfoSerializer(source="category", read_only=True)
    can_pin = serializers.SerializerMethodField()

    class Meta(PostBaseSerializer.Meta):
        fields = PostBaseSerializer.Meta.fields + [
            "author_info",
            "category_info",
            "can_pin",
        ]

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_can_pin(self, obj: Post) -> bool:
        """Returns can post be pinned by user or not"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.can_be_pinned_by(request.user)


class PostCreateUpdateSerializer(serializers.ModelSerializer[Post]):
    """Serializer for creating and updating posts"""

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "content",
            "image",
            "category",
            "publication_status",
        )
        read_only_fields = ("id", "slug")

    def create(self, validated_data: dict[str, Any]) -> Post:
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class PostPinningSerializer(serializers.Serializer):
    """Serializer for post pinning"""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any] | None:
        """General validation"""
        user = self.context["request"].user
        post = self.context["post"]

        # Check if user have active subscription
        if not hasattr(user, "subscription") or not user.subscription.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["Active subscription required to pin posts."]}
            )

        # Check if post is authored by user
        if post.author != user:
            raise serializers.ValidationError("You can only pin your own posts.")

        # Check if post is published
        if post.publication_status != Post.PUBLISHED:
            raise serializers.ValidationError("Only published posts can be pinned.")

        return attrs


class PostsByCategorySerializer(serializers.Serializer):
    """Serializer for correct display of posts_by_category view response data in OpenAPI."""

    category = CategorySerializer(read_only=True)
    posts = PostListSerializer(many=True, read_only=True)
    pinned_posts_count = serializers.IntegerField(read_only=True)


class FeaturedPostsSerializer(serializers.Serializer):
    """Serializer for correct display of featured_posts view response data in OpenAPI."""

    pinned = PostListSerializer(many=True, read_only=True)
    popular = PostListSerializer(many=True, read_only=True)
    total_pinned = serializers.IntegerField(read_only=True)


class TogglePostPinStatusSerializer(serializers.Serializer):
    """Serializer for correct display of toggle_post_pin_status view response data in OpenAPI."""

    msg = serializers.CharField(read_only=True)
    is_pinned = serializers.BooleanField(read_only=True)
    post = PostDetailSerializer(read_only=True)


class PinnedPostsOnlySerializer(serializers.Serializer):
    """Serializer for correct display of pinned_posts view response data in OpenAPI."""

    count = serializers.IntegerField(read_only=True)
    results = PostListSerializer(many=True, read_only=True)
