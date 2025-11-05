import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from app.models import TimeStampedModel


class Payment(TimeStampedModel):
    """Model for payment"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (SUCCEEDED, "Succeeded"),
        (CANCELLED, "Cancelled"),
        (FAILED, "Failed"),
        (REFUNDED, "Refunded"),
    ]

    STRIPE = "stripe"
    PAYPAL = "paypal"
    MANUAL = "manual"

    PAYMENT_METHOD_CHOICES = [
        (STRIPE, "Stripe"),
        (PAYPAL, "PayPal"),
        (MANUAL, "Manual"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    subscription = models.ForeignKey(
        "subscribe.Subscription",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=STRIPE,
    )

    # Stripe-specific fields
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_session_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    # Metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["stripe_payment_intent_id"]),
            models.Index(fields=["stripe_session_id"]),
            models.Index(fields=["created"]),
        ]

    def __str__(self) -> str:
        return (
            f"Payment {self.id} - {self.user.username} -${self.amount} ({self.status})"
        )

    @property
    def is_successful(self) -> bool:
        """Check if payment is successful"""
        return self.status == Payment.SUCCEEDED

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == Payment.PENDING

    @property
    def can_be_refunded(self) -> bool:
        """Check if payment can be refunded"""
        return (
            self.status == Payment.SUCCEEDED and self.payment_method == Payment.STRIPE
        )

    def mark_as_succeeded(self) -> None:
        """Mark payment as succeeded"""
        self.status = Payment.SUCCEEDED
        self.processed_at = timezone.now()
        self.save()

    def mark_as_failed(self, reason: str | None = None) -> None:
        """Mark payment as failed"""
        self.status = Payment.FAILED
        self.processed_at = timezone.now()
        if reason:
            self.metadata["failed_reason"] = reason
        self.save()


class PaymentAttempt(models.Model):
    """Model for payment attempt"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50)

    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_attempt"
        verbose_name = "Payment Attempt"
        verbose_name_plural = "Payment Attempts"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"Attempt for payment {self.payment.id} - {self.status}"


class Refund(models.Model):
    """Model for refund"""

    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (SUCCEEDED, "Succeeded"),
        (CANCELLED, "Cancelled"),
        (FAILED, "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="refunds",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    stripe_refund_id = models.CharField(max_length=255, null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_refunds",
    )

    created = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "refund"
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"Refund {self.id} - ${self.amount} for Payment {self.payment.id}"

    @property
    def is_partial(self) -> bool:
        """Check if refund is partial"""
        return self.amount < self.payment.amount

    def process_refund(self) -> None:
        self.status = self.SUCCEEDED
        self.processed_at = timezone.now()
        self.save()


class WebhookEvent(models.Model):
    """Model for webhook event of payment systems"""

    STRIPE = "stripe"
    PAYPAL = "paypal"

    PROVIDER_CHOICES = [
        (STRIPE, "Stripe"),
        (PAYPAL, "PayPal"),
    ]

    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    IGNORED = "ignored"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (PROCESSED, "Processed"),
        (FAILED, "Failed"),
        (IGNORED, "Ignored"),
    ]

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    data = models.JSONField()
    error_message = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "webhook_event"
        verbose_name = "Webhook Event"
        verbose_name_plural = "Webhook Events"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["provider", "event_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider} - {self.event_type} ({self.status})"

    def mark_as_processed(self) -> None:
        """Mark webhook event as processed"""
        self.status = self.PROCESSED
        self.processed_at = timezone.now()
        self.save()

    def mark_as_failed(self, error_message: str) -> None:
        """Mark webhook event as failed"""
        self.status = self.FAILED
        self.error_message = error_message
        self.processed_at = timezone.now()
        self.save()
