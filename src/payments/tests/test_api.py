from unittest.mock import patch
from uuid import uuid4

import pytest
import stripe
from django.urls import reverse

from accounts.models import User
from payments.api.serializers import (
    PaymentAnalyticsSerializer,
    PaymentSerializer,
    PaymentStatusSerializer,
    RefundSerializer,
    StripeCheckoutSessionSerializer,
)
from payments.models import Payment
from subscribe.models import Subscription, SubscriptionHistory

pytestmark = [pytest.mark.django_db]


class TestPaymentList:
    def test_permissions_not_authenticated(self, api):
        response = api.get(
            reverse("v1:payments:payment-list"), expected_status_code=401
        )

    def test_get_only(self, api, auth_user):
        response = api.get(reverse("v1:payments:payment-list"))
        response = api.post(
            reverse("v1:payments:payment-list"), expected_status_code=405
        )

    def test_get_fields(self, api, auth_user, payment_w_sub):
        response = api.get(reverse("v1:payments:payment-list"))
        response_results = response["results"]

        serializer = PaymentSerializer()
        expected_fields = serializer.fields

        assert payment_w_sub.subscription.user == auth_user

        for field in expected_fields:
            assert field in response_results[0]


class TestPaymentDetail:
    def test_permissions_not_authenticated(self, api, payment_w_sub):
        response = api.get(
            reverse(
                "v1:payments:payment-detail",
                kwargs={"pk": payment_w_sub.pk},
            ),
            expected_status_code=401,
        )

    def test_get_only(self, api, auth_user, payment_w_sub):
        response = api.get(
            reverse(
                "v1:payments:payment-detail",
                kwargs={"pk": payment_w_sub.pk},
            )
        )
        response = api.post(
            reverse(
                "v1:payments:payment-detail",
                kwargs={"pk": payment_w_sub.pk},
            ),
            expected_status_code=405,
        )

    def test_get_fields(self, api, auth_user, payment_w_sub):
        response = api.get(
            reverse(
                "v1:payments:payment-detail",
                kwargs={"pk": payment_w_sub.pk},
            )
        )

        serializer = PaymentSerializer()
        expected_fields = serializer.fields

        assert payment_w_sub.subscription.user == auth_user

        for field in expected_fields:
            assert field in response


class TestPaymentStatus:
    def test_permissions_not_authenticated(self, api, payment_w_sub):
        response = api.get(
            reverse(
                "v1:payments:payment-status",
                kwargs={"payment_id": payment_w_sub.pk},
            ),
            expected_status_code=401,
        )

    def test_no_payment(self, api, auth_user):
        response = api.get(
            reverse(
                "v1:payments:payment-status",
                kwargs={"payment_id": uuid4()},
            ),
            expected_status_code=404,
        )

    def test_not_users(self, api, auth_user, mixer):
        user_1 = mixer.blend(User)
        payment = mixer.blend(Payment, user=user_1)

        response = api.get(
            reverse(
                "v1:payments:payment-status",
                kwargs={"payment_id": payment.pk},
            ),
            expected_status_code=404,
        )

    def test_get_only(self, api, auth_user, payment_w_sub):
        response = api.get(
            reverse(
                "v1:payments:payment-status",
                kwargs={"payment_id": payment_w_sub.pk},
            )
        )
        response = api.post(
            reverse(
                "v1:payments:payment-status",
                kwargs={"payment_id": payment_w_sub.pk},
            ),
            expected_status_code=405,
        )

    def test_get_fields(self, api, auth_user, payment_w_sub):
        response = api.get(
            reverse(
                "v1:payments:payment-status",
                kwargs={"payment_id": payment_w_sub.pk},
            )
        )

        serializer = PaymentStatusSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response


class TestCancelPayment:
    def test_permissions_not_authenticated(self, api, payment_w_sub):
        response = api.post(
            reverse(
                "v1:payments:payment-cancel",
                kwargs={"payment_id": payment_w_sub.pk},
            ),
            expected_status_code=401,
        )

    def test_post_only(self, api, auth_user, payment_w_sub):
        response = api.get(
            reverse(
                "v1:payments:payment-cancel",
                kwargs={"payment_id": payment_w_sub.pk},
            ),
            expected_status_code=405,
        )
        response = api.post(
            reverse(
                "v1:payments:payment-cancel",
                kwargs={"payment_id": payment_w_sub.pk},
            )
        )

    def test_no_payment(self, api, auth_user):
        response = api.post(
            reverse(
                "v1:payments:payment-cancel",
                kwargs={"payment_id": uuid4()},
            ),
            expected_status_code=404,
        )

    def test_not_users(self, api, auth_user, mixer):
        user_1 = mixer.blend(User)
        payment = mixer.blend(Payment, user=user_1)

        response = api.post(
            reverse(
                "v1:payments:payment-cancel",
                kwargs={"payment_id": payment.pk},
            ),
            expected_status_code=404,
        )

    def test_not_pending(self, api, auth_user, mixer):
        payment = mixer.blend(Payment, user=auth_user, status=Payment.SUCCEEDED)

        response = api.post(
            reverse(
                "v1:payments:payment-cancel",
                kwargs={"payment_id": payment.pk},
            ),
            expected_status_code=400,
        )

        db_payment = Payment.objects.get(pk=payment.pk)

        assert db_payment.status == Payment.SUCCEEDED
        assert response["error"]

    def test_success(self, api, auth_user, payment_w_sub):
        assert payment_w_sub.status == Payment.PENDING
        assert payment_w_sub.subscription.status == Subscription.ACTIVE

        response = api.post(
            reverse(
                "v1:payments:payment-cancel",
                kwargs={"payment_id": payment_w_sub.pk},
            )
        )

        db_payment = Payment.objects.select_related("subscription").get(
            pk=payment_w_sub.pk
        )

        assert db_payment.status == Payment.CANCELLED
        assert db_payment.subscription.status == Subscription.CANCELLED

        assert response["message"]


class TestUserPaymentHistory:
    def test_permissions_not_authenticated(self, api, payment_w_sub):
        response = api.post(
            reverse("v1:payments:payment-history"),
            expected_status_code=401,
        )

    def test_get_only(self, api, auth_user):
        response = api.get(reverse("v1:payments:payment-history"))

        response = api.post(
            reverse("v1:payments:payment-history"),
            expected_status_code=405,
        )

    def test_not_users(self, api, auth_user, mixer):
        user_1 = mixer.blend(User)
        payment = mixer.blend(Payment, user=user_1)

        response = api.get(reverse("v1:payments:payment-history"))

        assert response["results"] == []
        assert response["count"] == 0

    def test_success_fields(self, api, auth_user, payment_w_sub):
        response = api.get(reverse("v1:payments:payment-history"))
        response_results = response["results"]

        serializer = PaymentSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]

        assert response["count"] == len(response_results)


class TestRetryPayment:
    def test_permissions_not_authenticated(self, api, payment_w_sub):
        response = api.post(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": payment_w_sub.pk},
            ),
            expected_status_code=401,
        )

    def test_post_only(self, api, auth_user):
        response = api.get(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": uuid4()},
            ),
            expected_status_code=405,
        )

    def test_no_payment(self, api, auth_user):
        response = api.post(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": uuid4()},
            ),
            expected_status_code=404,
        )
        assert response["error"]

    def test_not_users(self, api, auth_user, mixer):
        user_1 = mixer.blend(User)
        payment = mixer.blend(Payment, user=user_1, status=Payment.FAILED)

        response = api.post(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": payment.pk},
            ),
            expected_status_code=404,
        )
        assert response["error"]

    def test_not_status_failed(self, api, auth_user, mixer):
        user_1 = mixer.blend(User)
        payment_1 = mixer.blend(Payment, user=user_1, status=Payment.SUCCEEDED)
        payment_2 = mixer.blend(Payment, user=user_1, status=Payment.CANCELLED)

        response = api.post(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": payment_1.pk},
            ),
            expected_status_code=404,
        )
        assert response["error"]

        response = api.post(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": payment_2.pk},
            ),
            expected_status_code=404,
        )

        assert response["error"]

    @patch("payments.api.views.StripeService.create_checkout_session")
    def test_failed_checkout_creation(
        self, mock_create_checkout_session, api, auth_user, subscription, mixer
    ):
        mock_create_checkout_session.return_value = None

        payment = mixer.blend(
            Payment, user=auth_user, status=Payment.FAILED, subscription=subscription
        )

        response = api.post(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": payment.pk},
            ),
            expected_status_code=400,
        )
        assert response["error"]
        mock_create_checkout_session.assert_called_once()

    @patch("payments.api.views.StripeService.create_checkout_session")
    def test_success_fields(
        self, mock_create_checkout_session, api, auth_user, subscription, mixer
    ):

        payment = mixer.blend(
            Payment, user=auth_user, status=Payment.FAILED, subscription=subscription
        )
        mock_create_checkout_session.return_value = {
            "checkout_url": ".../payment/success?session_id=...",
            "session_id": 1234,
            "payment_id": payment.id,
        }

        response = api.post(
            reverse(
                "v1:payments:payment-retry",
                kwargs={"payment_id": payment.pk},
            ),
            expected_status_code=201,
        )

        serializer = StripeCheckoutSessionSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

        mock_create_checkout_session.assert_called_once()


class TestCheckoutSession:
    def test_permissions_not_authenticated(self, api):
        response = api.post(
            reverse("v1:payments:create-checkout-session"),
            expected_status_code=401,
        )

    def test_post_only(self, api, auth_user):
        response = api.get(
            reverse("v1:payments:create-checkout-session"),
            expected_status_code=405,
        )

    def test_user_has_active_subscription(
        self, api, auth_user, subscription_plan, subscription
    ):
        data = {
            "subscription_plan_id": subscription_plan.id,
            # etc default
        }

        response = api.post(
            reverse("v1:payments:create-checkout-session"),
            data=data,
            expected_status_code=400,  # serializer error
        )
        assert response["non_field_errors"]

    def test_user_has_pending_payment(self, api, auth_user, subscription_plan, mixer):
        payment_1 = mixer.blend(Payment, user=auth_user, status=Payment.PENDING)
        data = {
            "subscription_plan_id": subscription_plan.id,
            # etc default
        }

        response = api.post(
            reverse("v1:payments:create-checkout-session"),
            data=data,
            expected_status_code=400,  # serializer error
        )
        assert response["non_field_errors"]

    def test_no_subscription_plan(self, api, auth_user):
        data = {
            "subscription_plan_id": 123,
            # etc default
        }

        response = api.post(
            reverse("v1:payments:create-checkout-session"),
            data=data,
            expected_status_code=404,
        )

    @patch("payments.api.views.StripeService.create_checkout_session")
    def test_success(
        self, mock_create_checkout_session, api, auth_user, subscription_plan
    ):
        db_sub = Subscription.objects.filter(
            user=auth_user,
            plan=subscription_plan,
            status=Subscription.PENDING,
        ).first()
        assert db_sub is None

        mock_create_checkout_session.return_value = {
            "checkout_url": ".../payment/success?session_id=...",
            "session_id": 1234,
            "payment_id": uuid4(),
        }

        data = {
            "subscription_plan_id": subscription_plan.id,
            # etc default
        }
        response = api.post(
            reverse("v1:payments:create-checkout-session"),
            data=data,
            expected_status_code=201,
        )

        serializer = StripeCheckoutSessionSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response

        db_sub = Subscription.objects.filter(
            user=auth_user,
            plan=subscription_plan,
            status=Subscription.PENDING,
        ).first()
        assert db_sub is not None

        assert (
            Payment.objects.filter(
                user=auth_user,
                amount=subscription_plan.price,
            ).first()
            is not None
        )

        assert (
            SubscriptionHistory.objects.filter(
                subscription=db_sub,
                action=SubscriptionHistory.CREATED,
            ).first()
            is not None
        )
        mock_create_checkout_session.assert_called_once()


class TestRefundList:
    def test_permissions_not_authenticated(self, api):
        response = api.get(reverse("v1:payments:refund-list"), expected_status_code=401)

    def test_permissions_not_admin(self, api, auth_user):
        response = api.get(reverse("v1:payments:refund-list"), expected_status_code=403)

    def test_get_only(self, api, auth_admin_user):
        response = api.get(reverse("v1:payments:refund-list"))
        response = api.post(
            reverse("v1:payments:refund-list"), expected_status_code=405
        )

    def test_get_fields(self, api, auth_admin_user, refund):
        response = api.get(reverse("v1:payments:refund-list"))
        response_results = response["results"]

        serializer = RefundSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response_results[0]


class TestRefundDetail:
    def test_permissions_not_authenticated(self, api, refund):
        response = api.get(
            reverse(
                "v1:payments:refund-detail",
                kwargs={"pk": refund.pk},
            ),
            expected_status_code=401,
        )

    def test_permissions_not_admin(self, api, auth_user, refund):
        response = api.get(
            reverse(
                "v1:payments:refund-detail",
                kwargs={"pk": refund.pk},
            ),
            expected_status_code=403,
        )

    def test_get_only(self, api, auth_admin_user, refund):
        response = api.get(
            reverse(
                "v1:payments:refund-detail",
                kwargs={"pk": refund.pk},
            )
        )
        response = api.post(
            reverse(
                "v1:payments:refund-detail",
                kwargs={"pk": refund.pk},
            ),
            expected_status_code=405,
        )

    def test_get_fields(self, api, auth_admin_user, refund):
        response = api.get(
            reverse(
                "v1:payments:refund-detail",
                kwargs={"pk": refund.pk},
            )
        )

        serializer = RefundSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response


class TestPaymentAnalytics:
    def test_permissions_not_authenticated(self, api):
        response = api.get(
            reverse("v1:payments:payment-analytics"),
            expected_status_code=401,
        )

    def test_permissions_not_admin(self, api, auth_user):
        response = api.get(
            reverse("v1:payments:payment-analytics"),
            expected_status_code=403,
        )

    def test_get_only(self, api, auth_admin_user):
        response = api.get(
            reverse("v1:payments:payment-analytics"),
        )
        response = api.post(
            reverse("v1:payments:payment-analytics"),
            expected_status_code=405,
        )

    def test_get_fields(self, api, auth_admin_user):
        response = api.get(
            reverse("v1:payments:payment-analytics"),
        )

        serializer = PaymentAnalyticsSerializer()
        expected_fields = serializer.fields

        for field in expected_fields:
            assert field in response


# # Webhooks
# path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
class TestStripeWebhook:
    def test_post_only(self, api):
        response = api.api_client.get(reverse("v1:payments:stripe-webhook"))

        assert response.status_code == 405

    @patch("payments.api.views.stripe.Webhook.construct_event")
    @patch("payments.api.views.WebhookService.process_stripe_webhook")
    def test_success(self, mock_process_stripe_webhook, mock_construct_event, api):
        mock_construct_event.return_value = {
            "id": "some_id",
            "type": "some_type",
        }
        mock_process_stripe_webhook.return_value = True

        response = api.api_client.post(reverse("v1:payments:stripe-webhook"))

        assert response.status_code == 200
        mock_construct_event.assert_called_once()
        mock_process_stripe_webhook.assert_called_once()

    @patch("payments.api.views.WebhookService.process_stripe_webhook")
    def test_raise_on_not_valid_signature(
        self, mock_process_stripe_webhook, api, mocker
    ):
        mocker.patch(
            "stripe.WebhookSignature.verify_header",
            side_effect=stripe.SignatureVerificationError(
                "invalid signature", sig_header="not-valid-signature"
            ),
        )

        response = api.api_client.post(reverse("v1:payments:stripe-webhook"))

        assert response.status_code == 400
        mock_process_stripe_webhook.assert_not_called()
