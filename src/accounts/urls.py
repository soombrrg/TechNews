from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from accounts.api.views import (
    ChangePasswordView,
    LoginView,
    ProfileView,
    RegistrationView,
    logout_view,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "token/verify/",
        TokenVerifyView.as_view(),
        name="token_verify",  # Debug and token check
    ),
]
