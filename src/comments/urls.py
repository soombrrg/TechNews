from django.urls import path

from comments.api.views import (
    CommentDetailView,
    CommentListCreateView,
    UsersCommentsView,
    comment_replies,
    post_comments,
)

app_name = "comments"

urlpatterns = [
    path("", CommentListCreateView.as_view(), name="comment-list"),
    path("<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("users-comments/", UsersCommentsView.as_view(), name="users-comments"),
    path("post/<int:post_id>/", post_comments, name="post-comments"),
    path("<int:comment_id>/replies/", comment_replies, name="comment-replies"),
]
