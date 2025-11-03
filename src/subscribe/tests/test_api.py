from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from app.serializer import PinnedPostsListSerializer
from main.models import Post
from subscribe.api.serializers import (
    PinnedPostSerializer,
    SubscriptionHistorySerializer,
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    UserSubscriptionStatusSerializer,
)
from subscribe.models import (
    PinnedPost,
    Subscription,
    SubscriptionHistory,
    SubscriptionPlan,
)

pytestmark = [pytest.mark.django_db]


class TestSubscriptionPlanList:
    def test_only_get(self, api, subscription_plan):
        response = api.get(reverse("v1:subscribe:subscription-plan-list"))
        response = api.post(
            reverse("v1:subscribe:subscription-plan-list"),
            expected_status_code=405,
        )

    def test_get_fields(self, api, subscription_plan):
        response = api.get(reverse("v1:subscribe:subscription-plan-list"))
        response_results = response["results"]

        serializer = SubscriptionPlanSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]

    def test_only_active(self, api, mixer):
        subscription_plan_1 = mixer.blend(SubscriptionPlan, is_active=True)
        subscription_plan_2 = mixer.blend(SubscriptionPlan, is_active=False)
        response = api.get(reverse("v1:subscribe:subscription-plan-list"))

        # Only active plan should be listed
        assert len(response["results"]) == 1
        assert response["results"][0]["id"] == subscription_plan_1.id
        assert response["results"][0]["name"] == subscription_plan_1.name


class TestSubscriptionPlanDetail:
    def test_only_get(self, api, subscription_plan):
        response = api.get(
            reverse(
                "v1:subscribe:subscription-plan-detail",
                kwargs={"pk": subscription_plan.pk},
            ),
        )
        response = api.post(
            reverse(
                "v1:subscribe:subscription-plan-detail",
                kwargs={"pk": subscription_plan.pk},
            ),
            expected_status_code=405,
        )

    def test_get_fields(self, api, subscription_plan):
        response = api.get(
            reverse(
                "v1:subscribe:subscription-plan-detail",
                kwargs={"pk": subscription_plan.pk},
            )
        )

        serializer = SubscriptionPlanSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

    def test_only_active(self, api, mixer):
        subscription_plan_1 = mixer.blend(SubscriptionPlan, is_active=True)
        subscription_plan_2 = mixer.blend(SubscriptionPlan, is_active=False)
        response_1 = api.get(
            reverse(
                "v1:subscribe:subscription-plan-detail",
                kwargs={"pk": subscription_plan_1.pk},
            )
        )
        # Only active plan should be retrieved
        response_2 = api.get(
            reverse(
                "v1:subscribe:subscription-plan-detail",
                kwargs={"pk": subscription_plan_2.pk},
            ),
            expected_status_code=404,
        )


class TestUserSubscription:
    def test_permission_not_authenticated(self, api, subscription):
        response = api.get(
            reverse("v1:subscribe:my-subscription"),
            expected_status_code=401,
        )

    def test_only_get(self, api, auth_user, subscription):
        response = api.get(reverse("v1:subscribe:my-subscription"))
        response = api.post(
            reverse("v1:subscribe:my-subscription"),
            expected_status_code=405,
        )

    def test_get_fields(self, api, auth_user, subscription):
        response = api.get(reverse("v1:subscribe:my-subscription"))

        serializer = SubscriptionSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

    def test_no_subscription(self, api, auth_user):
        response = api.get(
            reverse("v1:subscribe:my-subscription"),
            expected_status_code=404,
        )
        assert response["detail"]


class TestSubscriptionStatus:
    def test_permission_not_authenticated(self, api, subscription):
        response = api.get(
            reverse("v1:subscribe:subscription-status"),
            expected_status_code=401,
        )

    def test_only_get(self, api, auth_user, subscription):
        response = api.get(reverse("v1:subscribe:subscription-status"))
        response = api.post(
            reverse("v1:subscribe:subscription-status"),
            expected_status_code=405,
        )

    def test_get_fields(self, auth_user, api, subscription):
        response = api.get(reverse("v1:subscribe:subscription-status"))
        serializer = UserSubscriptionStatusSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response


class TestSubscriptionHistory:
    def test_permission_not_authenticated(self, api, subscription):
        response = api.get(
            reverse("v1:subscribe:subscription-history"),
            expected_status_code=401,
        )

    def test_only_get(self, api, auth_user, subscription):
        response = api.get(reverse("v1:subscribe:subscription-history"))
        response = api.post(
            reverse("v1:subscribe:subscription-history"),
            expected_status_code=405,
        )

    def test_no_history(self, api, auth_user):
        response = api.get(reverse("v1:subscribe:subscription-history"))
        response_results = response["results"]

        assert len(response_results) == 0

    def test_get_fields(self, api, auth_user, subscription, history):
        response = api.get(reverse("v1:subscribe:subscription-history"))
        response_results = response["results"]

        serializer = SubscriptionHistorySerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]


class TestCancelSubscription:
    def test_permission_not_authenticated(self, api, subscription):
        response = api.post(
            reverse("v1:subscribe:cancel-subscription"),
            expected_status_code=401,
        )

    def test_no_subscription(self, api, auth_user):
        response = api.post(
            reverse("v1:subscribe:cancel-subscription"),
            expected_status_code=404,
        )
        assert response["error"]

    def test_only_post(self, api, auth_user, subscription):
        response = api.post(
            reverse("v1:subscribe:cancel-subscription"),
        )
        response = api.get(
            reverse("v1:subscribe:cancel-subscription"),
            expected_status_code=405,
        )

    def test_subscription_inactive(self, api, auth_user, subscription_plan, mixer):
        subscription = mixer.blend(
            Subscription,
            user=auth_user,
            status=Subscription.PENDING,
        )
        response = api.post(
            reverse("v1:subscribe:cancel-subscription"),
            expected_status_code=400,
        )
        assert response["error"]

    def test_success(self, api, auth_user, subscription, pinned_post):
        assert subscription.is_active
        record_exists = SubscriptionHistory.objects.filter(
            subscription=subscription, action=SubscriptionHistory.CANCELLED
        ).exists()
        assert not record_exists

        p_post_exists = PinnedPost.objects.filter(pk=pinned_post.pk).exists()
        assert p_post_exists

        response = api.post(reverse("v1:subscribe:cancel-subscription"))
        db_sub = Subscription.objects.get(pk=subscription.pk)

        assert response["msg"]
        # Subscription should be cancelled
        assert db_sub.status == db_sub.CANCELLED
        assert not db_sub.is_active

        # Pinned post if exists should be deleted
        p_post_exists = PinnedPost.objects.filter(pk=pinned_post.pk).exists()
        assert not p_post_exists

        # Record should be created on sub canceling
        record = SubscriptionHistory.objects.get(
            subscription=db_sub, action=SubscriptionHistory.CANCELLED
        )
        assert record


class TestPinnedPost:
    def test_permission_not_authenticated(self, api, pinned_post):
        response = api.get(
            reverse("v1:subscribe:my-pinned-post"),
            expected_status_code=401,
        )

    def test_fields(self, api, auth_user, pinned_post):
        # PinnedPostView uses same serializer for all methods
        response = api.get(reverse("v1:subscribe:my-pinned-post"))

        serializer = PinnedPostSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

    def test_get_no_pinned_post(self, api, auth_user):
        response = api.get(
            reverse("v1:subscribe:my-pinned-post"),
            expected_status_code=404,
        )
        assert response["detail"]

    def test_update_no_subscription(self, api, auth_user, post, mixer):
        post_to_pin = post.id
        data = {"post": post_to_pin}

        response = api.api_client.put(reverse("v1:subscribe:my-pinned-post"), data=data)
        response_data = response.json()

        assert response.status_code == 403
        assert response_data["error"]

    def test_update_no_active_subscription(
        self, api, auth_user, post, subscription_plan, mixer
    ):
        post_to_pin = post.id
        data = {"post": post_to_pin}
        subscription_1 = mixer.blend(
            Subscription,
            user=auth_user,
            plan=subscription_plan,
            status=Subscription.PENDING,
        )

        response = api.api_client.put(reverse("v1:subscribe:my-pinned-post"), data=data)
        response_data = response.json()

        assert response.status_code == 403
        assert response_data["error"]

    def test_delete_not_pinned_post(self, api, auth_user, mixer):
        response = api.api_client.delete(reverse("v1:subscribe:my-pinned-post"))
        response_data = response.json()

        assert response.status_code == 404
        assert response_data["error"]

    def test_delete_pinned_post(self, api, auth_user, pinned_post, mixer):
        db_p_post_exists = PinnedPost.objects.filter(pk=pinned_post.pk).exists()
        assert db_p_post_exists

        response = api.api_client.delete(reverse("v1:subscribe:my-pinned-post"))
        db_p_post_exists = PinnedPost.objects.filter(pk=pinned_post.pk).exists()

        assert response.status_code == 204
        assert not db_p_post_exists


class TestPinnedPostList:
    def test_only_get(self, api, pinned_post):
        response = api.get(reverse("v1:subscribe:pinned-posts-list"))

        response = api.post(
            reverse("v1:subscribe:pinned-posts-list"), expected_status_code=405
        )

    def test_success(self, api, subscribed_user_factory, category, mixer):
        user_1 = subscribed_user_factory()
        user_2 = subscribed_user_factory()

        post_1 = mixer.blend(Post, category=category, author=user_1)
        post_2 = mixer.blend(Post, category=category, author=user_2)

        pinned_post_1 = mixer.blend(PinnedPost, user=user_1, post=post_1)
        pinned_post_2 = mixer.blend(PinnedPost, user=user_2, post=post_2)

        response = api.get(reverse("v1:subscribe:pinned-posts-list"))

        serializer = PinnedPostsListSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

        assert response["count"] == len(response["results"]) == 2


class TestCanPinPost:
    def test_permission_not_authenticated(self, api, post):
        response = api.get(
            reverse("v1:subscribe:can-pin-post", kwargs={"post_id": post.id}),
            expected_status_code=401,
        )

    def test_only_get(self, api, auth_user, post):
        response = api.get(
            reverse("v1:subscribe:can-pin-post", kwargs={"post_id": post.id})
        )

        response = api.post(
            reverse("v1:subscribe:can-pin-post", kwargs={"post_id": post.id}),
            expected_status_code=405,
        )

    def test_no_post(self, api, auth_user):
        post_id = 1
        response = api.get(
            reverse("v1:subscribe:can-pin-post", kwargs={"post_id": post_id}),
            expected_status_code=404,
        )

        assert response["post_id"] == post_id
        assert response["can_pin"] == False
        assert response["checks"]["post_exists"] == False
        assert response["msg"]

    def test_no_subscription(self, api, auth_user, post, mixer):
        # If user have no active subscription -> can_pin == False
        post_id = post.id
        response = api.get(
            reverse("v1:subscribe:can-pin-post", kwargs={"post_id": post_id})
        )

        assert response["post_id"] == post_id
        assert response["can_pin"] == False
        assert response["checks"]
        assert response["msg"]

        assert response["checks"]["has_subscription"] == False

    def test_not_authored(self, api, auth_user, subscription, mixer):
        # If not authored by user -> can_pin == False
        user_1 = mixer.blend(User)
        post_1 = mixer.blend(Post, author=user_1)

        post_id = post_1.id
        response = api.get(
            reverse("v1:subscribe:can-pin-post", kwargs={"post_id": post_id})
        )

        assert response["post_id"] == post_id
        assert response["can_pin"] == False
        assert response["checks"]
        assert response["msg"]

        assert response["checks"]["is_authored"] == False

    def test_success(self, api, auth_user, subscription, post):
        post_id = post.id
        response = api.get(
            reverse("v1:subscribe:can-pin-post", kwargs={"post_id": post_id})
        )

        assert response["post_id"] == post_id
        assert response["can_pin"] == True
        assert response["checks"]
        assert response["msg"]

        expected_checks_fields = [
            "post_exists",
            "is_authored",
            "has_subscription",
            "has_active_subscription",
            "can_pin",
        ]

        for field in expected_checks_fields:
            assert field in response["checks"]
            assert response["checks"][field] == True
