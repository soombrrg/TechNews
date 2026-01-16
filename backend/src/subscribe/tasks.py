import logging
from typing import Any

from celery import shared_task
from django.utils import timezone

from subscribe.models import PinnedPost, Subscription, SubscriptionHistory

logger = logging.getLogger(__name__)


@shared_task
def check_expired_subscriptions() -> dict[str, Any]:
    """Periodic task for checking expired subscriptions"""
    now = timezone.now()

    expired_subscriptions = Subscription.objects.filter(
        status=Subscription.ACTIVE,
        end_date__lt=now,
    )

    expired_count = 0
    pinned_posts_removed = 0

    for subscription in expired_subscriptions:
        subscription.delete()
        expired_count += 1

        # Removing pinned post, if exists
        try:
            pinned_post = subscription.user.pinned_post
            pinned_post.delete()
            pinned_posts_removed += 1
        except PinnedPost.DoesNotExist:
            pass

        # Creating record in history
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action=SubscriptionHistory.EXPIRED,
            description="Subscription expired automatically.",
        )

    return {
        "expired_subscriptions": expired_count,
        "pinned_posts_removed": pinned_posts_removed,
    }


@shared_task
def send_subscription_expire_reminder() -> dict[str, Any]:
    """Sending notification about an expiring of subscription"""
    from datetime import timedelta

    from django.conf import settings
    from django.core.mail import send_mail

    # Finding subscriptions that will expire in 3 days
    reminder_date = timezone.now() + timedelta(hours=3)

    expiring_subscriptions = Subscription.objects.filter(
        status=Subscription.ACTIVE,
        end_date__date=reminder_date.date(),
        auto_renew=False,
    )

    sent_count = 0
    for subscription in expiring_subscriptions:
        try:
            send_mail(
                subject="Your subscription is expiring soon",
                message=f"Dear {subscription.user.get_full_name() or subscription.user.username},\n\n"
                f"Your {subscription.plan.name} subscription will expire on {subscription.end_date.strftime('%B %d, %Y')}.\n\n"
                f"To continue enjoying premium features, please renew your subscription.\n\n"
                f"Best regards, \nTechNews Team",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.user.email],
                fail_silently=False,
            )
            sent_count += 1
        except Exception as e:
            # Logging exception, but keep working
            logger.error("Failed to send email to %s: %s", subscription.user.email, e)
    return {
        "reminders_sent": sent_count,
    }
