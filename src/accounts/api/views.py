from typing import Any, Type

from django.contrib.auth import login
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.api.serializers import (
    ChangePasswordSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)
from accounts.models import User


class RegistrationView(generics.CreateAPIView):
    """Registration for new user"""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ["post"]

    def create(
        self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "msg": "User registered successfully",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """Login for user"""

    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        login(request, user)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "msg": "Logged in successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve and update User Profile"""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> AbstractBaseUser | AnonymousUser:
        return self.request.user

    def get_serializer_class(self) -> Type[Serializer]:
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserProfileSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """Changing user password"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> AbstractBaseUser | AnonymousUser:
        return self.request.user

    def update(
        self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "msg": "Password successfully changed.",
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    request={
        "application/json": {
            "properties": {
                "refresh_token": {
                    "type": "string",
                    "description": "Refresh token to blacklist",
                }
            },
        }
    },
    responses={
        200: {"properties": {"msg": {"type": "string"}}},
        400: {"properties": {"error": {"type": "string"}}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request: Request) -> Response:
    """Logout user"""
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({"msg": "Logged out successfully."}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
