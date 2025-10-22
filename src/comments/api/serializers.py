from typing import Any

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

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

    @staticmethod
    def get_author_info(obj: Comment) -> dict[str, Any]:
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

    def validate_parent(self, value: Comment) -> Comment | None:
        if value and value.post != self.initial_data.get("post"):
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

    def get_replies(self, obj: Comment) -> ReturnDict | list[Any]:
        # Displaying replies only for main comments
        if obj.parent is None:
            replies = obj.replies.filter(is_active=True).order_by("created")
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
