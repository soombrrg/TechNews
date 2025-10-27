from typing import TYPE_CHECKING, Any

from django.utils import timezone
from rest_framework import serializers

from subscribe.models import (
    PinnedPost,
    Subscription,
    SubscriptionHistory,
    SubscriptionPlan,
)

if TYPE_CHECKING:

    from main.models import Post


class SubscriptionPlanSerializer(serializers.ModelSerializer[SubscriptionPlan]):
    """Serializer for Subscription Plans"""

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "price",
            "duration_days",
            "features",
            "is_active",
            "created",
        ]
        read_only_fields = ["id", "created"]

    def to_representation(self, instance: SubscriptionPlan) -> dict[str, Any]:
        """Override for guarantee of correct output"""
        data = super().to_representation(instance)

        if data.get("features"):
            data["features"] = {}

        return data


class SubscriptionSerializer(serializers.ModelSerializer[Subscription]):
    """Serializer for Subscriptions"""

    plan_info = SubscriptionPlanSerializer(source="plan", read_only=True)
    user_info = serializers.SerializerMethodField()
    is_active = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            "id ",
            "user",
            "user_info",
            "plan",
            "plan_info",
            "status",
            "start_date",
            "end_date",
            "auto_renew",
            "is_active",
            "created",
            "modified",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "start_date",
            "end_date",
            "created",
            "modified",
        ]

    @staticmethod
    def get_user_info(obj: Subscription) -> dict[str, Any]:
        """Returns info about user"""
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "full_name": obj.user.full_name,
            "email": obj.user.email,
        }


class SubscriptionCreateSerializer(serializers.ModelSerializer[Subscription]):
    """Serializer for subscription creation"""

    class Meta:
        model = Subscription
        fields = ["plan"]

    def validate_plan(self, value: SubscriptionPlan) -> SubscriptionPlan | None:
        """Subscription plan validation"""
        if not value.is_active:
            raise serializers.ValidationError("Selected plan is not active.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any] | None:
        """General validation"""
        user = self.context["request"].user

        # Check if subscription is already active
        if hasattr(user, "subscription") and user.subscription.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["User already has an active subscription."]}
            )

        return attrs

    def create(self, validated_data: dict[str, Any]) -> Subscription:
        """Creates subscription"""
        validated_data["user"] = self.context["request"].user
        validated_data["status"] = Subscription.PENDING
        validated_data["start_date"] = timezone.now()
        validated_data["end_date"] = timezone.now()

        return super().create(validated_data)


class PinnedPostSerializer(serializers.ModelSerializer[PinnedPost]):
    """Serializer for pinned posts"""

    post_info = serializers.SerializerMethodField()

    class Meta:
        model = PinnedPost
        fields = [
            "id",
            "post",
            "post_info",
            "pinned_at",
        ]
        read_only_fields = ["id", "pinned_at"]

    @staticmethod
    def get_post_info(obj: PinnedPost) -> dict[str, Any] | None:
        """Returns info about post"""
        return {
            "id": obj.post.id,
            "title": obj.post.title,
            "slug": obj.post.slug,
            "content": obj.post.content,
            "image": obj.post.image,
            "views_count": obj.post.views_count,
            "created": obj.post.created,
        }

    def validate_post(self, value: "Post") -> "Post | None":
        """Post validation before pinning"""
        from main.models import Post

        user = self.context["request"].user

        # Check if post is authored by user
        if value.author != user:
            raise serializers.ValidationError("You can only pin your own posts.")

        # Check if post published
        if value.publication_status != Post.PUBLISHED:
            raise serializers.ValidationError("Only published posts can be pinned.")

        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any] | None:
        """General validation"""
        user = self.context["request"].user

        # Check if user have active subscription
        if not hasattr(user, "subscription") or not user.subscription.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["Active subscription required to pin posts."]}
            )

        return attrs

    def create(self, validated_data: dict[str, Any]) -> PinnedPost:
        """Creates pinned post"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class SubscriptionHistorySerializer(serializers.ModelSerializer[SubscriptionHistory]):
    """Serializer for subscription history"""

    class Meta:
        model = SubscriptionHistory
        fields = [
            "id",
            "action",
            "description",
            "metadata",
            "created",
        ]
        read_only_fields = ["id", "created"]


class UserSubscriptionStatusSerializer(serializers.Serializer):
    """Serializer for user subscription status"""

    has_subscription = serializers.BooleanField()
    is_active = serializers.BooleanField()
    can_pin_posts = serializers.BooleanField()
    subscription = SubscriptionSerializer(allow_null=True)
    pinned_post = PinnedPostSerializer(allow_null=True)

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """Creates response with info about user's subscription status"""
        user = self.context["request"].user
        has_subscription = hasattr(user, "subscription")
        subscription = user.subscription if has_subscription else None
        is_active = subscription.is_active if subscription else False
        pinned_post = getattr(user, "pinned_post", None) if is_active else None

        return {
            "has_subscription": has_subscription,
            "is_active": is_active,
            "can_pin_posts": is_active,
            "subscription": (
                SubscriptionSerializer(subscription).data if subscription else None
            ),
            "pinned_post": (
                PinnedPostSerializer(pinned_post).data if pinned_post else None
            ),
        }


class PostPinningSerializer(serializers.Serializer):
    """Serializer for post pinning"""

    post_id = serializers.IntegerField()

    def validate_post_id(self, value: int) -> int:
        """Validates post id"""
        from main.models import Post

        try:
            post = Post.objects.get(id=value, publication_status=Post.PUBLISHED)
        except Post.DoesNotExist:
            raise serializers.ValidationError("Post not found or not published.")

        user = self.context["request"].user
        if post.author != user:
            raise serializers.ValidationError("You can only pin your own posts.")

        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any] | None:
        """General validation"""
        user = self.context["request"].user

        # Check subscription
        if not hasattr(user, "subscription") or not user.subscription.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["Active subscription required to pin posts."]}
            )

        return attrs


class PostUnpinningSerializer(serializers.Serializer):
    """Serializer for post unpinning"""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any] | None:
        """General validation for post unpinning"""
        user = self.context["request"].user

        if not hasattr(user, "pinned_post"):
            raise serializers.ValidationError(
                {"non_field_errors": ["No pinned post found."]}
            )

        return attrs
