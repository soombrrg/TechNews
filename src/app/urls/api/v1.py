from django.urls import include, path

urlpatterns = [
    path("auth/", include("accounts.urls", namespace="auth")),
    path("posts/", include("main.urls", namespace="posts")),
]
