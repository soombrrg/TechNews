from typing import TYPE_CHECKING, Any, Type

from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from app.permissions import IsAuthorOrReadOnly
from main.api.serializers import (
    CategorySerializer,
    FeaturedPostsSerializer,
    PinnedPostsOnlySerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostPinningSerializer,
    PostsByCategorySerializer,
    TogglePostPinStatusSerializer,
)
from main.models import Category, Post

if TYPE_CHECKING:
    from django.contrib.auth.models import AnonymousUser
    from rest_framework.serializers import Serializer


class CategoryListCreateView(generics.ListCreateAPIView):
    """Api endpoint for listing and creating Categories"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created"]
    ordering = ["name"]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Api endpoint for concrete category"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = "slug"


class PostListCreateView(generics.ListCreateAPIView):
    """
    Api endpoint for listing and creating Posts with support for pinned posts.
    Pinned posts displayed first in "pinned_at" order.
    """

    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "title", "publication_status"]
    search_fields = ["title", "content"]
    ordering_fields = ["created", "modified", "views_count", "title"]
    ordering = ["-created"]

    def get_queryset(self) -> QuerySet[Post]:
        """Returning posts, depending on access right"""

        # Check for Swagger Schema generating
        if getattr(self, "swagger_fake_view", False):
            return Post.objects.none()

        queryset = Post.objects.select_related(
            "author", "category"
        ).with_comments_count()

        # Filter using access right
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(publication_status=Post.PUBLISHED)
        else:
            queryset = queryset.filter(
                Q(publication_status=Post.PUBLISHED) | Q(author=self.request.user)
            )

        # Check if ordering with dependence on pinned posts
        ordering = self.request.query_params.get("ordering", "")
        show_pinned_first = not ordering or ordering in ["-created", "created"]

        if show_pinned_first:
            return Post.objects.for_feed(
                Q(publication_status=Post.PUBLISHED)
                | (
                    Q(author=self.request.user)
                    if self.request.user.is_authenticated
                    else Q()
                )
            )

        return queryset

    def get_serializer_class(self) -> Type["Serializer"]:
        if self.request.method == "POST":
            return PostCreateUpdateSerializer
        return PostListSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().list(request, *args, **kwargs)

        # Adding Pinned posts stats
        if hasattr(response, "data") and "results" in response.data:
            pinned_count = sum(
                1 for post in response.data["results"] if post.get("is_pinned", False)
            )
            response.data["pinned_posts_count"] = pinned_count

        return response


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Api endpoint for concrete post"""

    queryset = Post.objects.select_related(
        "author", "category", "pin_info"
    ).with_comments_count()
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = "slug"

    def get_serializer_class(self) -> Type["Serializer"]:
        if self.request.method in ["PUT", "PATCH"]:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def retrieve(
        self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response:
        """Increasing views count on GET request"""
        instance = self.get_object()

        if request.method == "GET":
            instance.increment_views()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UsersPostsView(generics.ListAPIView):
    """Api endpoint for listing current user's posts"""

    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "publication_status"]
    search_fields = ["title", "content"]
    ordering_fields = ["created", "modified", "views_count", "title"]
    ordering = ["-created"]

    def get_queryset(self) -> QuerySet[Post]:
        # Check for Swagger Schema generating
        if getattr(self, "swagger_fake_view", False):
            return Post.objects.none()

        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(self.request.user, AnonymousUser):
                return Post.objects.none()

        return (
            Post.objects.filter(author=self.request.user)
            .select_related("category", "author")
            .with_comments_count()
        )


@extend_schema(responses=PostListSerializer(many=True))
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def popular_posts(request: Request) -> Response:
    """10 most popular Posts"""
    posts = (
        Post.objects.with_subscription_info()
        .filter(publication_status=Post.PUBLISHED)
        .with_comments_count()
        .order_by("-views_count")[:10]
    )

    serializer = PostListSerializer(
        posts,
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)


@extend_schema(responses=PostListSerializer(many=True))
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def recent_posts(request: Request) -> Response:
    """10 most recent Posts"""
    posts = (
        Post.objects.with_subscription_info()
        .filter(publication_status=Post.PUBLISHED)
        .with_comments_count()
        .order_by("-created")[:10]
    )

    serializer = PostListSerializer(
        posts,
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)


@extend_schema(responses=PostsByCategorySerializer)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def posts_by_category(request: Request, category_slug: str) -> Response:
    """Posts for defined category"""
    category = get_object_or_404(Category, slug=category_slug)

    # Retrieving posts depending on pinning
    posts = Post.objects.for_feed(
        category=category,
        publication_status=Post.PUBLISHED,
    )

    category_serializer = CategorySerializer(category)
    posts_serializer = PostListSerializer(
        posts,
        many=True,
        context={"request": request},
    )

    data = {
        "category": category_serializer.data,
        "posts": posts_serializer.data,
        "pinned_posts_count": sum(
            1 for post in posts_serializer.data if post.get("is_pinned", False)
        ),
    }

    return Response(data)


@extend_schema(responses=PinnedPostsOnlySerializer)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def pinned_posts_only(request: Request) -> Response:
    """Return pinned posts"""
    pinned_posts = Post.objects.pinned().with_comments_count()
    serializer = PostListSerializer(
        pinned_posts, many=True, context={"request": request}
    )
    return Response(
        {
            "count": len(pinned_posts),
            "results": serializer.data,
        }
    )


@extend_schema(responses=FeaturedPostsSerializer)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def featured_posts(request: Request) -> Response:
    """
    Recommended posts for main page:
    - Pinned posts (3 max)
    - Popular posts for last week
    """
    from datetime import timedelta  # noqa

    from django.utils import timezone  # noqa

    # Retrieving last 3 pinned posts
    pinned_posts = Post.objects.pinned().with_comments_count()[:3]

    # Retrieving popular posts (excluding pinned)
    week_ago = timezone.now() - timedelta(days=7)
    popular_posts_of_week = (
        Post.objects.with_subscription_info()
        .filter(
            publication_status=Post.PUBLISHED,
            created__gte=week_ago,
        )
        .exclude(
            id__in=[post.id for post in pinned_posts],
        )
        .with_comments_count()
        .order_by("-views_count")[:6]
    )

    pinned_serializer = PostListSerializer(
        pinned_posts,
        many=True,
        context={"request": request},
    )
    popular_serializer = PostListSerializer(
        popular_posts_of_week,
        many=True,
        context={"request": request},
    )

    data = {
        "pinned": pinned_serializer.data,
        "popular": popular_serializer.data,
        "total_pinned": Post.objects.pinned().count(),
    }

    return Response(data)


@extend_schema(
    request={"application/json": {"properties": {"slug": {"type": "string"}}}},
    responses={
        404: {"properties": {"error": {"type": "string"}}},
        400: {"properties": {"error": {"type": "string"}}},
        200: TogglePostPinStatusSerializer,
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def toggle_post_pin_status(request: Request, slug: str) -> Response:
    """Toggle pinned post status"""
    if TYPE_CHECKING:
        # Explicit type check for MyPy
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    post = get_object_or_404(Post, slug=slug, publication_status=Post.PUBLISHED)
    serializer = PostPinningSerializer(
        data=request.data, context={"request": request, "post": post}
    )

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            from subscribe.models import PinnedPost  # noqa

            if post.is_pinned:
                # Unpin if exists
                post.pin_info.delete()
                msg = "Post unpinned successfully"
                is_pinned = False
            else:
                # Deleting users existing pinned post before creating new
                if hasattr(request.user, "pinned_post"):
                    request.user.pinned_post.delete()

                # Creating new pinned post
                PinnedPost.objects.create(user=request.user, post=post)
                msg = "Post pinned successfully"
                is_pinned = True
            return Response(
                {
                    "msg": msg,
                    "is_pinned": is_pinned,
                    "post": PostDetailSerializer(
                        post, context={"request": request}
                    ).data,
                }
            )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
