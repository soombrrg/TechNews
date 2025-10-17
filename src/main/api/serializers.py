from django.utils.text import slugify
from rest_framework import serializers

from main.models import Category, Post


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category"""

    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "posts_count", "created"]
        read_only_fields = ["slug", "created"]

    def get_posts_count(self, obj) -> int:
        return obj.posts.filter(publication_status=Post.PUBLISHED).count()

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """Serializer for list of Posts"""

    author = serializers.StringReleatedField()
    category = serializers.StringReleatedField()
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

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # For Posts cards better viewing
        if len(data["content"]) > 200:
            data["content"] = data["content"][:200] + "..."
        return data


class PostDetailSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # For Post card convenient viewing
        if len(data["content"]) > 200:
            data["content"] = data["content"][:200] + "..."
        return data

    def get_author_info(self, obj) -> dict:
        author = obj.author
        return {
            "id": author.id,
            "username": author.username,
            "full_name": author.full_name,
            "avatar": author.avatar.url if author.avatar else None,
        }

    def get_category_info(self, obj) -> dict | None:
        try:
            category = obj.category
            return {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
            }
        except AttributeError:
            return None


class PostCreateUpdateSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        validated_data["slug"] = slugify(validated_data["title"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "title" in validated_data:
            validated_data["slug"] = slugify(validated_data["title"])
        return super().update(instance, validated_data)
