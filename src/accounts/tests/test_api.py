# TODO
# path("login/", LoginView.as_view(), name="login"),
# path("logout/", logout_view, name="logout"),
# path("profile/", ProfileView.as_view(), name="profile"),
# path("change-password/", ChangePasswordView.as_view(), name="change_password"),
# path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


import pytest
from django.urls import reverse

from accounts.models import User

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend(User)


class TestRegistration:
    @pytest.mark.xfail
    def test_register_get(self, api):
        response = api.get(reverse("auth:register"))

    def test_register_post_w_invalid_data(self, api):
        data = {
            "username": "user",
            "email": "user@u",
            "password": "u",
            "password_confirmation": "user12",
            "first_name": "",
            "last_name": "last_name",
        }
        response = api.api_client.post(reverse("auth:register"), data=data)
        assert response.status_code == 400

    def test_register_post_w_valid_data(self, api):
        data = {
            "username": "user",
            "email": "user@mail.ru",
            "password": "user123456",
            "password_confirmation": "user123456",
            "first_name": "first_name",
            "last_name": "last_name",
        }
        response = api.api_client.post(reverse("auth:register"), data=data)
        response_data = response.data
        supposed_keys = ["user", "refresh", "access", "msg"]

        assert response.status_code == 201

        # Test structure of response data
        assert all(key in response_data.keys() for key in supposed_keys)
        assert response_data["msg"] == "User registered successfully"

        assert response_data["user"]["username"] == data["username"]
        assert response_data["user"]["email"] == data["email"]
        assert response_data["user"]["first_name"] == data["first_name"]
        assert response_data["user"]["last_name"] == data["last_name"]

        # Test computed fields
        supposed_full_name = f"{data["first_name"]} {data["last_name"]}".strip()
        assert response_data["user"]["full_name"] == supposed_full_name
        assert response_data["user"]["posts_count"] == 0
        assert response_data["user"]["comments_count"] == 0
