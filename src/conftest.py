from typing import Any

import pytest
from django.contrib.auth.hashers import make_password
from mixer.backend.django import mixer as _mixer

from accounts.models import User
from app.test.api_clients import AppClient
from main.models import Category, Post


@pytest.fixture
def api() -> AppClient:
    return AppClient()


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def user(mixer) -> User:
    return mixer.blend(
        User, password=make_password("valid_password"), avatar="avatar.png"
    )


@pytest.fixture
def auth_user(api, user: User) -> User:
    api.api_client.force_authenticate(user)
    return user


@pytest.fixture
def category_factory(mixer):
    def _factory(**kwargs: dict[str, Any]) -> Category:
        return mixer.blend(Category, **kwargs)

    return _factory


@pytest.fixture
def post_factory(mixer):
    def _factory(**kwargs: dict[str, Any]) -> Post:
        return mixer.blend(Post, **kwargs)

    return _factory


@pytest.fixture
def category(mixer) -> Category:
    return mixer.blend(Category)


@pytest.fixture
def post(mixer, category: Category, user: User) -> Post:
    return mixer.blend(Post, category=category, author=user)
