from typing import Any

from django.utils.text import slugify
from rest_framework import serializers

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

    def get_posts_count(self, obj: Category) -> int:
        return obj.posts.filter(publication_status=Post.PUBLISHED).count()

    def create(self, validated_data: dict[str, Any]) -> Category:
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer[Post]):
    """Serializer for list of Posts"""

    author = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    comments_count = serializers.ReadOnlyField()

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
        ]
        read_only_fields = ["slug", "author", "views_count"]

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
    """Serializer for detail of Post"""

    author_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    comments_count = serializers.ReadOnlyField()

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
        ]
        read_only_fields = ["slug", "author", "views_count"]

    def create(self, validated_data: dict[str, Any]) -> Post:
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def to_representation(self, instance: Post) -> dict[str, Any]:
        data = super().to_representation(instance)
        # For Post card convenient viewing
        if len(data["content"]) > 200:
            data["content"] = data["content"][:200] + "..."
        return data

    def get_author_info(self, obj: Post) -> dict[str, Any]:
        author = obj.author
        return {
            "id": author.id,
            "username": author.username,
            "full_name": author.full_name,
            "avatar": author.avatar.url if author.avatar else None,
        }

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
