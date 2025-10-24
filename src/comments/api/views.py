from typing import TYPE_CHECKING, Type

from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from app.permissions import IsAuthorOrReadOnly
from comments.api.serializers import (
    CommentCreateSerializer,
    CommentDetailSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
)
from comments.models import Comment
from main.models import Post


class CommentListCreateView(generics.ListCreateAPIView):
    """Listing and creating comments"""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = ["post", "author", "parent"]
    search_fields = ["content"]
    ordering_fields = ["created", "modified"]
    ordering = ["-created"]

    def get_queryset(self) -> QuerySet[Comment]:
        return Comment.objects.filter(is_active=True).select_related(
            "post", "author", "parent"
        )

    def get_serializer_class(self) -> Type[Serializer]:
        if self.request.method == "POST":
            return CommentCreateSerializer
        else:
            return CommentSerializer


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Detail view for retrieve, update, and delete comment"""

    permission_classes = [IsAuthorOrReadOnly]
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.filter(is_active=True).select_related("author", "post")

    def get_serializer_class(self) -> Type[Serializer]:
        if self.request.method in ["PUT", "PATCH"]:
            return CommentUpdateSerializer
        return CommentDetailSerializer

    def perform_destroy(self, instance: Comment) -> None:
        # Soft deletion - mark as inactive
        instance.is_active = False
        instance.save()


class UsersCommentsView(generics.ListAPIView):
    """Comments of current user"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["post", "parent", "is_active"]
    search_fields = ["content"]
    ordering_fields = ["created", "modified"]
    ordering = ["-created"]

    def get_queryset(self) -> QuerySet[Comment]:
        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(self.request.user, AnonymousUser):
                return Comment.objects.none()

        return Comment.objects.filter(author=self.request.user).select_related(
            "post", "parent"
        )


@extend_schema(
    responses={
        "post": {
            "id": {"type": "int"},
            "title": {"type": "string"},
            "slug": {"type": "string"},
        },
        "comments": CommentSerializer(many=True),
        "comments_count": {"type": "int"},
    }
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def post_comments(request: Request, post_id: int) -> Response:
    """GET comments of certain post"""
    post = get_object_or_404(Post, id=post_id, publication_status=Post.PUBLISHED)

    # Fetching only main comments
    comments = (
        Comment.objects.filter(
            post=post,
            is_active=True,
            parent=None,
        )
        .select_related("author")
        .prefetch_related("replies__author")
        .order_by("-created")
    )

    comments_serializer = CommentSerializer(
        comments, many=True, context={"request": request}
    )
    return Response(
        {
            "post": {
                "id": post.pk,
                "title": post.title,
                "slug": post.slug,
            },
            "comments": comments_serializer.data,
            "comments_count": post.comments_count,
        }
    )


@extend_schema(
    responses={
        "parent_comment": CommentSerializer(),
        "replies": CommentSerializer(many=True),
        "replies_count": {"type": "int"},
    }
)
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def comment_replies(request: Request, comment_id: int) -> Response:
    """GET comment`s replies"""
    parent_comment = get_object_or_404(Comment, id=comment_id)

    replies = (
        Comment.objects.filter(parent=parent_comment, is_active=True)
        .select_related("author")
        .order_by("-created")
    )

    parent_comment_serializer = CommentSerializer(
        parent_comment, context={"request": request}
    )
    replies_serializer = CommentSerializer(
        replies, many=True, context={"request": request}
    )

    return Response(
        {
            "parent_comment": parent_comment_serializer.data,
            "replies": replies_serializer.data,
            "replies_count": replies.count(),
        }
    )
