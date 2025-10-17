from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("auth/", include("accounts.urls", namespace="auth")),
    path("posts/", include("main.urls", namespace="posts")),
    # Swagger
    path(
        "docs/schema/",
        SpectacularAPIView.as_view(api_version="v1"),
        name="schema",
    ),
    # Optional UI:
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="v1:schema"),
    ),
    path(
        "docs/redoc/",
        SpectacularRedocView.as_view(url_name="v1:schema"),
    ),
]
