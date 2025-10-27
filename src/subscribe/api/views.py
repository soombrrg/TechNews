from typing import TYPE_CHECKING, Any

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from main.models import Post
from subscribe.api.serializers import (
    PinnedPostSerializer,
    SubscriptionHistorySerializer,
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    UserSubscriptionStatusSerializer,
)
from subscribe.models import (
    PinnedPost,
    Subscription,
    SubscriptionHistory,
    SubscriptionPlan,
)


class SubscriptionPlanListView(generics.ListAPIView):
    """List of available subscription plans"""

    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    """Detail info of available subscription plan"""

    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class UserSubscriptionView(generics.RetrieveAPIView):
    """Info of current user's subscription"""

    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Subscription | None:
        """Returns current user's subscription"""
        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(self.request.user, AnonymousUser):
                return None

        try:
            return self.request.user.subscription
        except Subscription.DoesNotExist:
            return None

    def retrieve(
        self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response:
        """Retrieves info of current user's subscription"""
        subscription = self.get_object()
        if subscription is None:
            return Response(
                {"detail": "Subscription not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(subscription)
        return Response(serializer.data)


class SubscriptionHistoryView(generics.ListAPIView):
    """History of changes of user`s subscription"""

    serializer_class = SubscriptionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[SubscriptionHistory]:
        """Returns current user's subscription history"""
        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(self.request.user, AnonymousUser):
                return SubscriptionHistory.objects.none()

        try:
            subscription = self.request.user.subscription
            return subscription.history.all()
        except Subscription.DoesNotExist:
            return SubscriptionHistory.objects.none()


class PinnedPostView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete of user`s pinned post"""

    serializer_class = PinnedPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> PinnedPost | None:
        """Returns current user's pinned post"""
        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(self.request.user, AnonymousUser):
                return None

        try:
            return self.request.user.pinned_post
        except PinnedPost.DoesNotExist:
            return None

    def retrieve(
        self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response:
        """Retrieves info of current user's pinned post"""
        pinned_post = self.get_object()
        if pinned_post is None:
            return Response(
                {"detail": "Pinned post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(pinned_post)
        return Response(serializer.data)

    def update(
        self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response:
        """Updates current user's pinned post"""
        # Check subscription
        if (
            not hasattr(request.user, "subscription")
            or not request.user.subscription.is_active
        ):
            return Response(
                {"error": "Active subscription required to pin posts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    def destroy(
        self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response:
        """Deletes current user`s pinned post"""
        pinned_post = self.get_object()
        if pinned_post is None:
            return Response(
                {"error": "Pinned post not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        pinned_post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def subscription_status(request: Request) -> Response:
    """Returns current user's subscription status"""
    serializer = UserSubscriptionStatusSerializer(request.user)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def pin_post(request: Request) -> Response:
    """Pins user`s post"""
    serializer = PinnedPostSerializer(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    post_id = serializer.validated_data["post_id"]
    try:
        with transaction.atomic():
            post = get_object_or_404(
                Post, id=post_id, publication_status=Post.PUBLISHED
            )

            # Check if authored by user
            if post.author != request.user:
                return Response(
                    {"error": "You can only pin your own posts."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check subscription
            if (
                not hasattr(request.user, "subscription")
                or not request.user.subscription.is_active
            ):
                return Response(
                    {"error": "Active subscription required to pin posts."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Delete current pinned post if exist
            if hasattr(request.user, "pinned_post"):
                request.user.pinned_post.delete()

            if TYPE_CHECKING:
                # Explicit type check for MyPy
                if isinstance(request.user, AnonymousUser):
                    return Response(status=status.HTTP_401_UNAUTHORIZED)

            pinned_post = PinnedPost.objects.create(
                user=request.user,
                post=post,
            )
            response_serializer = PinnedPostSerializer(pinned_post)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def unpin_post(request: Request) -> Response:
    """Unpins user`s post"""
    serializer = PinnedPostSerializer(data=request.data, context={"request": request})

    if TYPE_CHECKING:
        # Explicit type check for MyPy
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        pinned_post = request.user.pinned_post
        pinned_post.delete()

        return Response(
            {"msg": "Post unpinned successfully"},
            status=status.HTTP_200_OK,
        )
    except PinnedPost.DoesNotExist:
        return Response(
            {"error": "Pinned post not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def cancel_subscription(request: Request) -> Response:
    """Cancel user`s subscription"""
    try:
        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(request.user, AnonymousUser):
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        subscription = request.user.subscription

        if not subscription.is_active:
            return Response(
                {"error": "No active subscription found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Cancelling subscription
            subscription.cancel()

            # Deleting pinned post if exist
            if hasattr(request.user, "pinned_post"):
                request.user.pinned_post.delete()

            # Write down in history
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action=SubscriptionHistory.CANCELLED,
                description="Subscription canceled by user.",
            )
        return Response(
            {"msg": "Subscription cancelled successfully."},
            status=status.HTTP_200_OK,
        )

    except Subscription.DoesNotExist:
        return Response(
            {"error": "Subscription not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def pinned_posts_list(request: Request) -> Response:
    """Retrieves list of all pinned posts"""
    # Retrieve pinned post only from user`s with active subscription
    pinned_posts = (
        PinnedPost.objects.select_related(
            "post",
            "post__author",
            "post__category",
            "user__subscription",
        )
        .filter(
            user__subscription__status=Subscription.ACTIVE,
            user__subscription__end_date__gt=timezone.now(),
            post__publication_status=Post.PUBLISHED,
        )
        .order_by("pinned_at")
    )

    # Creating response with info about post
    posts_data = []
    for pinned_post in pinned_posts:
        post = pinned_post.post
        posts_data.append(
            {
                "id": post.id,
                "title": post.title,
                "slug": post.slug,
                "content": (
                    post.content[:200] + "..."
                    if len(post.content) > 200
                    else post.content
                ),
                "image": post.image.url if post.image else None,
                "category": post.category.name if post.category else None,
                "author": {
                    "id": post.author.id,
                    "username": post.author.username,
                    "full_name": post.author.full_name,
                },
                "views_count": post.views_count,
                "comments_count": post.comments_count,
                "created": post.created,
                "pinned_at": pinned_post.pinned_at,
                "is_pinned": True,
            }
        )

    return Response(
        {
            "count": len(posts_data),
            "results": posts_data,
        }
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def can_pin_post(request: Request, post_id: int) -> Response:
    """Check if user can pin post with given id"""
    try:
        post = get_object_or_404(Post, id=post_id, publication_status=Post.PUBLISHED)

        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(request.user, AnonymousUser):
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        checks = {
            "post_exists": True,
            "is_authored": post.author == request.user,
            "has_subscription": hasattr(request.user, "subscription"),
            "has_active_subscription": False,
            "can_pin": False,
        }
        if checks["has_subscription"]:
            checks["has_active_subscription"] = request.user.subscription.is_active

        checks["can_pin"] = (
            checks["is_authored"]
            and checks["has_subscription"]
            and checks["has_active_subscription"]
        )

        return Response(
            {
                "post_id": post_id,
                "can_pin": checks["can_pin"],
                "checks": checks,
                "msg": "Can pin post." if checks["can_pin"] else "Can`t pin post.",
            }
        )

    except Post.DoesNotExist:
        return Response(
            {
                "post_id": post_id,
                "can_pin": False,
                "checks": {"post_exists": False},
                "msg": "Post not found.",
            },
            status.HTTP_404_NOT_FOUND,
        )
