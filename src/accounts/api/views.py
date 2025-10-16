from django.contrib.auth import login
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
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

    def create(self, request, *args, **kwargs):
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

    def post(self, request, *args, **kwargs):
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

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserProfileSerializer


class ChangePasswordView(generics.UpdateAPIView):
    """Changing user password"""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "msg": "Password successfully changed.",
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout user"""
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({"msg": "Logged out successfully."}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
