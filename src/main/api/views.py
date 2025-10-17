from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from main.api.serializers import (
    CategorySerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)
from main.models import Category, Post
from main.permissions import IsAuthorOrReadOnly


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
    """Api endpoint for listing and creating Posts"""

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

    def get_queryset(self):
        """Returning posts, depending on access right"""
        queryset = Post.objects.select_related("auther", "category")

        # Filter using access right
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(publication_status=Post.PUBLISHED)
        else:
            queryset = queryset.filter(
                Q(publication_status=Post.PUBLISHED) | Q(author=self.request.user)
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer
        return PostListSerializer


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Api endpoint for concrete post"""

    queryset = Post.objects.select_related("auther", "category")
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Increasing views count on GET request"""
        instance = self.get_object()

        if request.method == "GET":
            instance.increment_views()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserPostsView(generics.ListAPIView):
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

    def get_queryset(self):
        # Check for Swagger Schema generating
        if getattr(self, "swagger_fake_view", False):
            return Post.objects.none()

        return Post.objects.filter(author=self.request.user).select_related(
            "category", "author"
        )


@extend_schema(
    responses={
        "category": CategorySerializer(),
        "posts": PostListSerializer(many=True),
    }
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def posts_by_category(request, category_slug):
    """Post for defined category"""
    category = get_object_or_404(Category, slug=category_slug)
    posts = (
        Post.objects.filter(category=category, publication_status=Post.PUBLISHED)
        .select_related("author", "category")
        .order_by("-created")
    )

    category_serializer = CategorySerializer(category)
    posts_serializer = PostListSerializer(
        posts,
        many=True,
        context={"request": request},
    )

    return Response(
        {
            "category": category_serializer.data,
            "posts": posts_serializer.data,
        }
    )


@extend_schema(responses=PostListSerializer(many=True))
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def popular_posts(request):
    """10 most popular Posts"""
    posts = (
        Post.objects.filter(publication_status=Post.PUBLISHED)
        .select_related("author", "category")
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
def recent_posts(request):
    """10 most recent Posts"""
    posts = (
        Post.objects.filter(publication_status=Post.PUBLISHED)
        .select_related("author", "category")
        .order_by("-created")[:10]
    )

    serializer = PostListSerializer(
        posts,
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)
