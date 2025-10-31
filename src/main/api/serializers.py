from typing import Any

from django.utils.text import slugify
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from app.serializer import AuthorInfoSerializer, CategoryInfoSerializer
from main.models import Category, Post


class CategorySerializer(serializers.ModelSerializer[Category]):
    """Serializer for Category"""

    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "posts_count",
            "created",
        ]
        read_only_fields = ["slug", "created"]

    @extend_schema_field(OpenApiTypes.INT)
    def get_posts_count(self, obj: Category) -> int:
        return obj.posts.filter(publication_status=Post.PUBLISHED).count()

    def create(self, validated_data: dict[str, Any]) -> Category:
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer[Post]):
    """Serializer for list of Posts"""

    author = serializers.StringRelatedField()  # type: ignore[var-annotated]
    category = serializers.StringRelatedField()  # type: ignore[var-annotated]
    comments_count = serializers.ReadOnlyField()
    is_pinned = serializers.ReadOnlyField()
    pinned_info = serializers.SerializerMethodField()

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
            "created",
            "modified",
            "is_pinned",
            "pinned_info",
        ]
        read_only_fields = ["slug", "author", "views_count"]

    def get_pinned_info(self, obj: Post) -> dict[str, Any]:
        """Returns info about post pinning"""
        return obj.get_pinned_info()

    def create(self, validated_data: dict[str, Any]) -> Post:
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def to_representation(self, instance: Post) -> dict[str, Any]:
        data = super().to_representation(instance)
        # For Posts cards better viewing
        if len(data["content"]) > 200:
            data["content"] = data["content"][:200] + "..."
        return data


class PostDetailSerializer(serializers.ModelSerializer[Post]):
    """Serializer for Post details"""

    author_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    comments_count = serializers.ReadOnlyField()
    is_pinned = serializers.ReadOnlyField()
    pinned_info = serializers.SerializerMethodField()
    can_pin = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "image",
            "author",
            "author_info",
            "category",
            "category_info",
            "publication_status",
            "comments_count",
            "views_count",
            "created",
            "modified",
            "is_pinned",
            "pinned_info",
            "can_pin",
        ]
        read_only_fields = ["slug", "author", "views_count"]

    def get_pinned_info(self, obj: Post) -> dict[str, Any]:
        """Returns info about post pinning"""
        return obj.get_pinned_info()

    def get_can_pin(self, obj: Post) -> bool:
        """Returns can post be pinned by user or not"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.can_be_pinned_by(request.user)

    def create(self, validated_data: dict[str, Any]) -> Post:
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def to_representation(self, instance: Post) -> dict[str, Any]:
        data = super().to_representation(instance)
        # For Post card convenient viewing
        if len(data["content"]) > 200:
            data["content"] = data["content"][:200] + "..."
        return data

    @extend_schema_field(AuthorInfoSerializer)
    def get_author_info(self, obj: Post) -> dict[str, Any]:
        author = obj.author
        return {
            "id": author.id,
            "username": author.username,
            "full_name": author.full_name,
            "avatar": author.avatar.url if author.avatar else None,
        }

    @extend_schema_field(CategoryInfoSerializer)
    def get_category_info(self, obj: Post) -> dict[str, Any] | None:
        category = getattr(obj, "category", None)
        if category is not None:
            return {
                "id": category.pk,
                "name": category.name,
                "slug": category.slug,
            }
        return None


class PostCreateUpdateSerializer(serializers.ModelSerializer[Post]):
    """Serializer for creating and updating posts"""

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "image",
            "category",
            "publication_status",
        )

    def create(self, validated_data: dict[str, Any]) -> Post:
        validated_data["author"] = self.context["request"].user
        validated_data["slug"] = slugify(validated_data["title"])
        return super().create(validated_data)

    def update(self, instance: Post, validated_data: dict[str, Any]) -> Post:
        if "title" in validated_data:
            validated_data["slug"] = slugify(validated_data["title"])
        return super().update(instance, validated_data)


class PostsByCategorySerializer(serializers.Serializer):
    """Serializer for correct display of posts_by_category view response data in OpenAPI."""

    category = CategorySerializer(read_only=True)
    posts = PostListSerializer(many=True, read_only=True)


class FeaturedPostsSerializer(serializers.Serializer):
    """Serializer for correct display of featured_posts view response data in OpenAPI."""

    pinned = PostListSerializer(many=True, read_only=True)
    popular_posts = PostListSerializer(many=True, read_only=True)
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
