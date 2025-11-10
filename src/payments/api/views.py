from typing import TYPE_CHECKING
from uuid import UUID

import stripe
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from payments.api.serializers import (
    PaymentAnalyticsSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
    PaymentStatusSerializer,
    RefundCreateSerializer,
    RefundSerializer,
    StripeCheckoutSessionSerializer,
    UserPaymentHistorySerializer,
)
from payments.models import Payment, Refund
from payments.services import PaymentService, StripeService, WebhookService
from subscribe.models import SubscriptionPlan

if TYPE_CHECKING:

    from django.contrib.auth.models import AnonymousUser


class PaymentBase(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_base_queryset(self) -> QuerySet[Payment]:
        """Returns payments of current user."""
        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(self.request.user, AnonymousUser):
                return Payment.objects.none()

        # Check for Swagger Schema generating
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()

        return Payment.objects.filter(user=self.request.user).select_related(
            "subscription", "subscription__plan"
        )


class PaymentListView(PaymentBase, generics.ListAPIView):
    """List of user payments."""

    def get_queryset(self) -> QuerySet[Payment]:
        return super().get_base_queryset().order_by("-created")


class PaymentDetailView(PaymentBase, generics.RetrieveAPIView):
    """Detail information about a payment."""

    def get_queryset(self) -> QuerySet[Payment]:
        return super().get_base_queryset()


@extend_schema(
    request=PaymentCreateSerializer,
    responses={
        200: StripeCheckoutSessionSerializer,
        404: {"properties": {"error": {"type": "string"}}},
        400: {"properties": {"error": {"type": "string"}}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_checkout_session_view(request: Request) -> Response:
    """Create Stripe Checkout session of subscription payment."""
    if TYPE_CHECKING:
        # Explicit type check for MyPy
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = PaymentCreateSerializer(
        data=request.data,
        context={"request": request},
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    plan_id = serializer.validated_data["subscription_plan_id"]
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    try:
        with transaction.atomic():
            # Creating payment and subscription
            payment, subscription = PaymentService.create_subscription_payment(
                request.user, plan
            )

            # Retrieving URLs
            success_url = serializer.validated_data.get(
                "success_url",
                f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            )
            cancel_url = serializer.validated_data.get(
                "cancel_url",
                f"{settings.FRONTEND_URL}/payment/cancel",
            )

            # Creating Stripe session
            session_data = StripeService.create_checkout_session(
                payment, success_url, cancel_url
            )

            if session_data is None:
                return Response(
                    {"error": "Failed to created checkout session"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            response_serializer = StripeCheckoutSessionSerializer(session_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request={
        "application/json": {
            "properties": {"payment_id": {"type": "string", "format": "uuid"}}
        }
    },
    responses={
        404: {"properties": {"error": {"type": "string"}}},
        400: {"properties": {"error": {"type": "string"}}},
        200: PaymentStatusSerializer,
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def payment_status(request: Request, payment_id: "UUID") -> Response:
    """Check payment status of current user."""
    if TYPE_CHECKING:
        # Explicit type check for MyPy
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)

        # If session_id exists, checking status in Stripe
        if payment.stripe_session_id and payment.status in [
            Payment.PENDING,
            Payment.PROCESSING,
        ]:
            session_info = StripeService.retrieve_session(payment.stripe_session_id)

            if session_info:
                if session_info["status"] == "complete":
                    PaymentService.process_successful_payment(payment)
                if session_info["status"] == "failed":
                    PaymentService.process_failed_payment(payment, "Session failed")

        response_data = {
            "payment_id": payment.id,
            "status": payment.status,
            "message": f"Payment is {payment.status}.",
            "subscription_activated": False,
        }

        if payment.is_successful and payment.subscription:
            response_data["subscription_activated"] = payment.subscription.is_active

        serializer = PaymentStatusSerializer(response_data)
        return Response(serializer.data)

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@extend_schema(
    request={
        "application/json": {
            "properties": {"payment_id": {"type": "string", "format": "uuid"}}
        }
    },
    responses={
        404: {"properties": {"error": {"type": "string"}}},
        400: {"properties": {"error": {"type": "string"}}},
        200: {"properties": {"message": {"type": "string"}}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def cancel_payment(request: Request, payment_id: "UUID") -> Response:
    """Cancel payment for current user."""
    if TYPE_CHECKING:
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)

        if not payment.is_pending:
            return Response(
                {"error": "Can cancel only pending payments."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = Payment.CANCELLED
        payment.save()

        # Canceling subscription
        if payment.subscription:
            payment.subscription.cancel()

        return Response({"message": "Payment cancelled successfully."})

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


class RefundBaseView(generics.GenericAPIView):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_base_queryset(self) -> QuerySet[Refund]:
        if TYPE_CHECKING:
            # Explicit type check for MyPy
            if isinstance(self.request.user, AnonymousUser):
                return Refund.objects.none()

        # Check for Swagger Schema generating
        if getattr(self, "swagger_fake_view", False):
            return Refund.objects.none()

        return Refund.objects.all().select_related(
            "payment", "payment__user", "created_by"
        )


class RefundListView(RefundBaseView, generics.ListAPIView):
    """List of refunds for administrators only."""

    def get_queryset(self) -> QuerySet[Refund]:
        return super().get_base_queryset().order_by("-created")


class RefundDetailView(RefundBaseView, generics.RetrieveAPIView):
    """Detail information about a refund."""

    def get_queryset(self) -> QuerySet[Refund]:
        return super().get_base_queryset()


@extend_schema(
    request=RefundCreateSerializer,
    responses={
        404: {"properties": {"error": {"type": "string"}}},
        400: {"properties": {"error": {"type": "string"}}},
        200: PaymentStatusSerializer,
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def create_refund(request: Request, payment_id: "UUID") -> Response:
    """Create new refund for payment."""
    try:
        payment = Payment.objects.get(id=payment_id)

        if not payment.can_be_refunded:
            return Response(
                {"error": "Payment can't be refunded."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RefundCreateSerializer(
            data=request.data,
            context={"payment_id": payment_id},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Creating refund
            refund = serializer.save(
                payment=payment,
                created_by=request.user,
            )

            # Handling refund through Stripe
            success = StripeService.refund_payment(
                payment,
                refund.amount,
                refund.reason,
            )

            if not success:
                refund.status = Refund.FAILED
                refund.save()
                return Response(
                    {"error": "Failed to process refund."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refund.process_refund()
            # If this is full refund, canceling subscription
            if refund.amount == payment.amount and payment.subscription:
                PaymentService.cancel_subscription(payment.subscription)

            response_serializer = RefundSerializer(refund)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@extend_schema(exclude=True)
@csrf_exempt
@require_POST
def stripe_webhook(request: Request) -> HttpResponse:
    """Webhook endpoint for Stripe"""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        # Verifying webhook
        event = stripe.Webhook.construct_event(  # type: ignore
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        # Incorrect payload
        return HttpResponse(status=400)
    except stripe.SignatureVerificationError:
        # Incorrect signature
        return HttpResponse(status=400)

    # Handling event
    success = WebhookService.process_stripe_webhook(event)

    if not success:
        return HttpResponse(status=400)
    return HttpResponse(status=200)


@extend_schema(responses=PaymentAnalyticsSerializer)
@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def payment_analytics(request: Request) -> Response:
    """Analytic of payment for administrators only."""
    analytics = PaymentService.get_payment_analytics()
    return Response(analytics)


@extend_schema(
    responses={
        200: UserPaymentHistorySerializer,
    },
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def user_payment_history(request: Request) -> Response:
    """History of payment history for current user."""
    if TYPE_CHECKING:
        # Explicit type check for MyPy
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    payments = (
        Payment.objects.filter(user=request.user)
        .select_related("subscription", "subscription__plan")
        .order_by("-created")
    )

    serializer = PaymentSerializer(payments, many=True)
    return Response(
        {
            "count": len(payments),
            "results": serializer.data,
        }
    )


@extend_schema(
    request={
        "application/json": {
            "properties": {"payment_id": {"type": "string", "format": "uuid"}}
        }
    },
    responses={
        200: StripeCheckoutSessionSerializer,
        404: {"properties": {"error": {"type": "string"}}},
    },
)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def retry_payment(request: Request, payment_id: "UUID") -> Response:
    """Retry payment."""
    if TYPE_CHECKING:
        # Explicit type check for MyPy
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    try:
        payment = Payment.objects.select_related(
            "subscription", "subscription__plan"
        ).get(
            id=payment_id,
            user=request.user,
            status=Payment.FAILED,
        )

        # Retrieving URLs
        success_url = request.data.get(
            "success_url",
            f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        )
        cancel_url = request.data.get(
            "cancel_url",
            f"{settings.FRONTEND_URL}/payment/cancel",
        )

        # Creating Stripe session
        session_data = StripeService.create_checkout_session(
            payment, success_url, cancel_url
        )

        if session_data is None:
            return Response(
                {"error": "Failed to created checkout session"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_serializer = StripeCheckoutSessionSerializer(session_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND
        )
