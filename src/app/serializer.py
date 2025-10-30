from rest_framework import serializers


class AuthorInfoSerializer(serializers.Serializer):
    """Serializer for correct display of author info in OpenAPI."""

    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    avatar = serializers.URLField(read_only=True, allow_null=True)


class CategoryInfoSerializer(serializers.Serializer):
    """Serializer for correct display of category info in OpenAPI."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)


class PostInfoSerializer(serializers.Serializer):
    """Serializer for correct display of post info in OpenAPI."""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    content = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True, allow_null=True)

    views_count = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(read_only=True)


class PinnedPostDataSerializer(PostInfoSerializer):
    """Serializer for correct display of pinned post data in OpenAPI."""

    category = serializers.CharField(read_only=True)
    author = AuthorInfoSerializer(read_only=True)

    comments_count = serializers.IntegerField(read_only=True)

    pinned_at = serializers.DateTimeField(read_only=True)
    is_pinned = serializers.BooleanField(read_only=True)


class PinnedPostsListSerializer(serializers.Serializer):
    """Serializer for correct display of pinned_posts_list view response data in OpenAPI."""

    count = serializers.IntegerField(read_only=True)
    results = PinnedPostDataSerializer(many=True, read_only=True)
