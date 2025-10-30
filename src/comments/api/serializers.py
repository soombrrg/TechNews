from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from app.serializer import AuthorInfoSerializer
from comments.models import Comment
from main.models import Post


class CommentSerializer(serializers.ModelSerializer[Comment]):
    """Base serializer for Comments"""

    author_info = serializers.SerializerMethodField()
    replies_count = serializers.ReadOnlyField()
    is_reply = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "author",
            "author_info",
            "parent",
            "is_active",
            "is_reply",
            "replies_count",
            "created",
            "modified",
        ]
        read_only_fields = ["author", "is_active"]

    @extend_schema_field(AuthorInfoSerializer)
    def get_author_info(self, obj: Comment) -> dict[str, Any]:
        return {
            "id": obj.author.id,
            "username": obj.author.username,
            "full_name": obj.author.full_name,
            "avatar": obj.author.avatar.url if obj.author.avatar else None,
        }


class CommentCreateSerializer(serializers.ModelSerializer[Comment]):
    """Serializer for Comments creation"""

    class Meta:
        model = Comment
        fields = [
            "post",
            "parent",
            "content",
        ]

    def validate_post(self, value: Post) -> Post | None:
        # Check if post exists before creating comment
        if not Post.objects.filter(
            id=value.pk,
            publication_status=Post.PUBLISHED,
        ).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_parent(self, value: Comment | None) -> Comment | None:
        # Comment can be without parent
        if not value:
            return value

        post_data = self.initial_data.get("post")
        if not post_data:
            return value

        # If parent provided -> checking belonging to the same post
        if value.post.id != int(post_data):
            raise serializers.ValidationError(
                "Parent comment must belong to the same post."
            )
        return value

    def create(self, validated_data: dict[str, Any]) -> Comment:
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer[Comment]):
    """Serializer for Comments update"""

    class Meta:
        model = Comment
        fields = ["content"]


class CommentDetailSerializer(CommentSerializer):
    """Detail serializer for Comments with responses"""

    replies = serializers.SerializerMethodField()

    class Meta(CommentSerializer.Meta):
        fields = CommentSerializer.Meta.fields + ["replies"]

    @extend_schema_field(serializers.ListSerializer(child=CommentSerializer()))
    def get_replies(self, obj: Comment) -> ReturnDict | list[Any]:
        # Displaying replies only for main comments
        if obj.parent is None:
            replies = obj.replies.filter(is_active=True).order_by("created")
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class PostDataSerializer(serializers.Serializer):
    """Serializer for correct display of post data in OpenAPI."""

    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)


class PostCommentsSerializer(serializers.Serializer):
    """Serializer for correct display of post_comments view response data in OpenAPI."""

    post = PostDataSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.IntegerField(read_only=True)


class CommentRepliesSerializer(serializers.Serializer):
    """Serializer for correct display of comment_replies view response data in OpenAPI."""

    parent_comment = CommentSerializer(read_only=True)
    replies = CommentSerializer(many=True, read_only=True)
    replies_count = serializers.IntegerField(read_only=True)
