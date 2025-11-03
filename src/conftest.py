from datetime import timedelta
from typing import Any

import pytest
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from mixer.backend.django import mixer as _mixer

from accounts.models import User
from app.test.api_clients import AppClient
from comments.models import Comment
from main.models import Category, Post
from subscribe.models import (
    PinnedPost,
    Subscription,
    SubscriptionHistory,
    SubscriptionPlan,
)


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
def category(mixer) -> Category:
    return mixer.blend(Category)


@pytest.fixture
def post(mixer, category: Category, user: User) -> Post:
    return mixer.blend(Post, category=category, author=user)


@pytest.fixture
def comment(mixer, category: Category, user: User, post: Post) -> Comment:
    return mixer.blend(Comment, category=category, author=user, post=post)


@pytest.fixture
def subscription_plan(mixer) -> SubscriptionPlan:
    return mixer.blend(SubscriptionPlan)


@pytest.fixture
def subscription(
    mixer, user: User, subscription_plan: SubscriptionPlan
) -> Subscription:
    return mixer.blend(
        Subscription,
        user=user,
        plan=subscription_plan,
        status=Subscription.ACTIVE,
        end_date=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def pinned_post(
    mixer, user: User, subscription: Subscription, post: Post
) -> PinnedPost:
    return mixer.blend(PinnedPost, user=user, post=post)


@pytest.fixture
def history(mixer, subscription: Subscription) -> SubscriptionHistory:
    return mixer.blend(SubscriptionHistory, subscription=subscription)


@pytest.fixture
def subscribed_user_factory(mixer, subscription_plan):
    def _factory(**kwargs: dict[str, Any]) -> User:
        sub_user = mixer.blend(User)
        subscription = mixer.blend(
            Subscription,
            user=sub_user,
            plan=subscription_plan,
            status=Subscription.ACTIVE,
            end_date=timezone.now() + timedelta(days=30),
        )
        return sub_user

    return _factory
