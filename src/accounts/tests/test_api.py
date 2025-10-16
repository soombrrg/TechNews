import pytest
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend(
        User, password=make_password("valid_password"), avatar="avatar.png"
    )


@pytest.fixture
def auth_user(api, user):
    api.api_client.force_authenticate(user)
    return user


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
        expected_fields = ["user", "refresh", "access", "msg"]

        assert response.status_code == 201
        # Test structure of response data
        assert all(key in response_data for key in expected_fields)
        assert response_data["msg"] == "User registered successfully"

        data.pop("password")
        data.pop("password_confirmation")
        for key in data:
            assert response_data["user"][key] == data[key]

        # Test computed fields
        supposed_full_name = f"{data['first_name']} {data['last_name']}".strip()
        assert response_data["user"]["full_name"] == supposed_full_name
        assert response_data["user"]["posts_count"] == 0
        assert response_data["user"]["comments_count"] == 0


class TestLogin:
    def test_success(self, api, user):
        data = {"email": user.email, "password": "valid_password"}
        response = api.api_client.post(reverse("auth:login"), data=data)

        expected_fields = [
            "user",
            "refresh",
            "access",
            "msg",
        ]

        assert response.status_code == 200
        for key in expected_fields:
            assert key in response.data
        assert response.data["msg"] == "Logged in successfully."

    def test_user_disabled(self, api, user):
        user.is_active = False
        data = {
            "email": user.email,
            "password": "valid_password",
        }
        response = api.api_client.post(reverse("auth:login"), data=data)
        assert response.status_code == 400

    def test_password_not_provided(self, api, user):
        data = {
            "email": user.email,
        }
        response = api.api_client.post(reverse("auth:login"), data=data)
        assert response.status_code == 400

    def test_invalid_password(self, api, user):
        data = {
            "email": user.email,
            "password": "wrongpassword",
        }
        response = api.api_client.post(reverse("auth:login"), data=data)
        assert response.status_code == 400

    def test_invalid_username(self, api, user):
        data = {
            "email": "wronguser",
            "password": user.password,
        }
        response = api.api_client.post(reverse("auth:login"), data=data)
        assert response.status_code == 400


class TestProfile:
    def test_get_not_authenticated(self, api, user):
        response = api.get(reverse("auth:profile"), expected_status_code=401)

    def test_get_success(self, api, auth_user):
        response = api.get(reverse("auth:profile"))
        expected_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "bio",
            "posts_count",
            "comments_count",
            "created",
            "modified",
        ]
        for key in expected_fields:
            assert key in response

    @pytest.mark.parametrize("method", ["put", "patch"])
    def test_update(self, api, auth_user, method):
        data = {
            "first_name": "first_name",
            "last_name": "last_name",
            "avatar": "",
            "bio": "bio",
        }
        if method == "put":
            response = api.api_client.put(reverse("auth:profile"), data=data)

        if method == "patch":
            response = api.api_client.patch(reverse("auth:profile"), data=data)

        assert response.status_code == 200
        assert response.data["avatar"] is None
        for key in data:
            assert key in response.data


class TestLogout:
    def test_not_authenticated(self, api, user):
        response = api.api_client.post(reverse("auth:logout"))
        assert response.status_code == 401

    def test_successfully(self, api, auth_user):
        refresh = RefreshToken.for_user(auth_user)

        response = api.api_client.post(
            reverse("auth:logout"), data={"refresh_token": refresh}
        )

        assert response.status_code == 200
        assert response.data["msg"] == "Logged out successfully."

        assert BlacklistedToken.objects.filter(token__jti=refresh["jti"]).exists()

        response = api.api_client.post(
            reverse("auth:logout"), data={"refresh_token": refresh}
        )
        assert response.status_code == 400
        assert response.data["error"] == "Invalid token."

    def test_invalid_token(self, api, auth_user):

        response = api.api_client.post(
            reverse("auth:logout"), data={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 400
        assert response.data["error"] == "Invalid token."


class TestChangePassword:
    def test_not_authenticated(self, api, user):
        response = api.api_client.put(reverse("auth:change_password"), data={})
        assert response.status_code == 401

    @pytest.mark.parametrize("method", ["put", "patch"])
    @pytest.mark.parametrize(
        "data, validity",
        [
            (
                {
                    "old_password": "valid_password",
                    "new_password": "new_password",
                    "new_password_confirmation": "new_password",
                },
                True,
            ),
            (
                {
                    "old_password": "invalid_pssd",
                    "new_password": "new_password",
                    "new_password_confirmation": "n",
                },
                False,
            ),
        ],
    )
    def test_success(self, api, auth_user, method, data, validity):
        old_hashed_password = auth_user.password
        if method == "put":
            response = api.api_client.put(reverse("auth:change_password"), data=data)

        if method == "patch":
            response = api.api_client.patch(reverse("auth:change_password"), data=data)

        new_password = User.objects.get(username=auth_user.username).password
        if validity:
            assert response.status_code == 200
            assert new_password != old_hashed_password
            assert "msg" in response.data
        else:
            assert response.status_code == 400
            assert new_password == old_hashed_password
