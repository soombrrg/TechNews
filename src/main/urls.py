from django.urls import path

from main.api.views import (
    CategoryDetailView,
    CategoryListCreateView,
    PostDetailView,
    PostListCreateView,
    UserPostsView,
    popular_posts,
    posts_by_category,
    recent_posts,
)

app_name = "main"

urlpatterns = [
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path(
        "categories/<slug:category_slug>/posts/",
        posts_by_category,
        name="posts-by-category",
    ),
    # Posts
    path("", PostListCreateView.as_view(), name="post-list"),
    path("user-posts/", UserPostsView.as_view(), name="user-posts"),
    path("popular/", popular_posts, name="popular-posts"),
    path("recent/", recent_posts, name="recent-posts"),
    path("<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
]
