from typing import Any

from django.db.models import Sum
from rest_framework import serializers

from payments.models import Payment, PaymentAttempt, Refund, WebhookEvent


class PaymentSerializer(serializers.ModelSerializer[Payment]):
    """Serializer for Payments"""

    user_info = serializers.SerializerMethodField()
    subscription_info = serializers.SerializerMethodField()
    is_successful = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    can_be_refunded = serializers.ReadOnlyField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_info",
            "subscription",
            "subscription_info",
            "description",
            "amount",
            "currency",
            "status",
            "payment_method",
            "is_pending",
            "is_successful",
            "can_be_refunded",
            "is_pending",
            "created",
            "modified",
            "processed_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "created",
            "modified",
            "processed_at",
        ]

    def get_user_info(self, obj: Payment) -> dict[str, Any]:
        """Return information about user"""
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }

    def get_subscription_info(self, obj: Payment) -> dict[str, Any] | None:
        """Return information about subscription"""
        if obj.subscription:
            return {
                "id": obj.subscription.id,
                "plan_name": obj.subscription.plan.name,
                "start_date": obj.subscription.start_date,
                "end_date": obj.subscription.end_date,
                "status": obj.subscription.status,
            }
        return None


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for Payment creation"""

    subscription_plan_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES, default=Payment.STRIPE
    )
    success_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)

    def validate_subscription_plan_id(self, value: int) -> int:
        """Validate subscription plan id"""
        from subscribe.models import SubscriptionPlan

        try:
            plan = SubscriptionPlan.objects.get(id=value, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid subscription plan id. ")

        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """General validation"""
        user = self.context["request"].user

        # Check if already has subscription
        if hasattr(user, "subscription") and user.subscription.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": "User already has active subscription."}
            )

        # Check if having pending payments
        pending_payments_exists = Payment.objects.filter(
            user=user, status__in=[Payment.PENDING, Payment.PROCESSING]
        ).exists()

        if pending_payments_exists:
            raise serializers.ValidationError(
                {
                    "non_field_errors": "User has pending payments. Please complete or cancel them first."
                }
            )

        return attrs


class PaymentAttemptSerializer(serializers.ModelSerializer[PaymentAttempt]):
    """Serializer for Payment attempts"""

    class Meta:
        model = PaymentAttempt
        fields = [
            "id",
            "stripe_charge_id",
            "status",
            "error_message",
            "metadata",
            "created",
        ]
        read_only_fields = ["id", "created"]


class RefundSerializer(serializers.ModelSerializer[Refund]):
    """Serializer for Refund"""

    payment_info = serializers.SerializerMethodField()
    created_by_info = serializers.SerializerMethodField()
    is_partial = serializers.ReadOnlyField()

    class Meta:
        model = Refund
        fields = [
            "id",
            "payment",
            "payment_info",
            "amount",
            "reason",
            "status",
            "is_partial",
            "created_by",
            "created_by_info",
            "created",
            "processed_at",
        ]
        read_only_fields = ["id", "status", "created", "processed_at"]

    def get_payment_info(self, obj: Refund) -> dict[str, Any]:
        """Return information about payment"""
        return {
            "id": obj.payment.id,
            "amount": obj.payment.amount,
            "currency": obj.payment.currency,
            "status": obj.payment.status,
            "user": obj.payment.user.username,
        }

    def get_created_by_info(self, obj: Refund) -> dict[str, Any] | None:
        """Return information about user that created the refund"""
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
            }
        return None

    def validate_amount(self, value: int) -> int:
        """Validate amount"""
        if value <= 0:
            raise serializers.ValidationError("Refund amount must be positive.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """General validation"""
        payment_id = self.context.get("payment_id")
        if payment_id:
            try:
                payment = Payment.objects.get(id=payment_id)
            except Payment.DoesNotExist:
                raise serializers.ValidationError("Payment not found.")

            if not payment.can_be_refunded:
                raise serializers.ValidationError("This payment can not be refunded.")

            # Check if sum of refund is bigger than payment amount
            total_refund = (
                payment.refunds.filter(status=Refund.SUCCEEDED).aggregate(
                    total=Sum("amount")
                )["total"]
                or 0
            )

            if attrs["amount"] > (payment.amount - total_refund):
                raise serializers.ValidationError(
                    "Refund amount is greater than remaining payment amount."
                )
        return attrs


class RefundCreateSerializer(serializers.ModelSerializer[Refund]):
    """Serializer for Refund creation"""

    class Meta:
        model = Refund
        fields = ["amount", "reason"]

    def validate_amount(self, value: int) -> int:
        """Validate refund amount"""
        if value <= 0:
            raise serializers.ValidationError("Refund amount must be positive.")
        return value


class WebhookEventSerializer(serializers.ModelSerializer[WebhookEvent]):
    """Serializer for WebhookEvent"""

    class Meta:
        model = WebhookEvent
        fields = [
            "id",
            "provider",
            "event_id",
            "event_type",
            "status",
            "processed_at",
            "error_message",
            "created",
        ]
        read_only_fields = ["id", "created"]


class StripeCheckoutSessionSerializer(serializers.Serializer):
    """Serializer for Stripe Checkout Session"""

    checkout_url = serializers.URLField(read_only=True)
    session_id = serializers.IntegerField(read_only=True)
    payment_id = serializers.IntegerField(read_only=True)


class PaymentStatusSerializer(serializers.Serializer):
    """Serializer for Payment Status"""

    payment_id = serializers.IntegerField()
    status = serializers.CharField()
    message = serializers.CharField()
    subscription_activated = serializers.BooleanField(default=False)
