from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from app.serializer import AuthorInfoSerializer
from comments.models import Comment
from main.models import Post


class CommentSerializer(serializers.ModelSerializer[Comment]):
    """Base serializer for Comments"""

    post = serializers.StringRelatedField(source="post.slug", read_only=True)  # type: ignore[var-annotated]
    author_info = AuthorInfoSerializer(source="author", read_only=True)
    replies_count = serializers.IntegerField(read_only=True)
    is_reply = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
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


class CommentCreateSerializer(serializers.ModelSerializer[Comment]):
    """Serializer for Comments creation"""

    post_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = [
            "post_id",
            "parent",
            "content",
        ]

    def validate_post_id(self, value: Post) -> Post | None:
        # Check if post exists before creating comment
        try:
            post = Post.objects.only("id", "title").get(
                id=value,
                publication_status=Post.PUBLISHED,
            )
            self.context["post"] = post
            return value
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found.")

    def validate_parent(self, value: Comment | None) -> Comment | None:
        # Comment can be without parent
        if not value:
            return value

        post_data = self.initial_data.get("post_id")

        # If parent provided -> checking belonging to the same post
        if value.post.id != int(post_data):
            raise serializers.ValidationError(
                "Parent comment must belong to the same post."
            )
        return value

    def create(self, validated_data: dict[str, Any]) -> Comment:
        validated_data["author"] = self.context["request"].user
        validated_data["post"] = self.context["post"]
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
            replies = obj.replies.all()
            return CommentSerializer(replies, many=True).data
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
