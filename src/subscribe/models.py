import uuid
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone

from app.models import TimeStampedModel


class SubscriptionPlan(TimeStampedModel):
    """Model for subscription plan"""

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    stripe_price_id = models.CharField(max_length=255, unique=True)
    features = models.JSONField(
        default=dict,
        help_text="List of subscription plan's features",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subscription_plan"
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ["price"]

    def __str__(self) -> str:
        return f"{self.name} - ${self.price}"


class Subscription(TimeStampedModel):
    """Model for subscription"""

    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Canceled"),
        (PENDING, "Pending"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    auto_renew = models.BooleanField(default=True)

    class Meat:
        db_table = "subscriptions"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["end_date", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.plan.name} ({self.status})"

    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        return self.status == self.ACTIVE and self.end_date > timezone.now()

    @property
    def days_remaining(self) -> int:
        """Returns number of days before subscription ending"""
        if not self.is_active:
            return 0

        delta = self.end_date - timezone.now()
        return max(0, delta.days)

    def extend(self, days: int = 30) -> None:
        """Extend subscription plan using days number"""
        if self.is_active:
            self.end_date += timedelta(days=days)
        else:
            self.start_date = timezone.now()
            self.end_date = self.start_date + timedelta(days=days)
            self.status = self.ACTIVE
        self.save()

    def cancel(self) -> None:
        """Mark subscription as cancelled"""
        self.status = self.CANCELLED
        self.auto_renew = False
        self.save()

    def expire(self) -> None:
        """Mark subscription as expired"""
        self.status = self.EXPIRED
        self.save()

    def activate(self) -> None:
        """Mark subscription as active"""
        self.status = self.ACTIVE
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        self.save()


class PinnedPost(models.Model):
    """Model for pinned post"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pinned_post",
    )
    post = models.OneToOneField(
        "main.Post",
        on_delete=models.CASCADE,
        related_name="pin_info",
    )
    pinned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pinned_post"
        verbose_name = "Pinned Post"
        verbose_name_plural = "Pinned Posts"
        ordering = ["pinned_at"]
        indexes = [models.Index(fields=["pinned_at"])]

    def __str__(self) -> str:
        return f"{self.user.username} pinned: {self.post.title}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Overrides save for checking subscription"""

        # Check existence of active subscription
        if (
            not hasattr(self.user, "subscription")
            or not self.user.subscription.is_active
        ):
            raise ValueError("User must have an active subscription to pin posts.")

        # Check that post belongs to user
        if self.post.author != self.user:
            raise ValueError("You can only pin there own posts.")

        super().save(*args, **kwargs)


class SubscriptionHistory(models.Model):
    """Model for history of subscription changing"""

    CREATED = "created"
    ACTIVATED = "activated"
    RENEWED = "renewed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FAILED = "failed"

    ACTION_CHOICES = [
        (CREATED, "created"),
        (ACTIVATED, "activated"),
        (RENEWED, "renewed"),
        (CANCELLED, "cancelled"),
        (EXPIRED, "expired"),
        (FAILED, "failed"),
    ]

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="history",
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subscription_history"
        verbose_name = "Subscription History"
        verbose_name_plural = "Subscription History"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.subscription.user.username} - {self.action}"
