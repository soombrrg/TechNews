from typing import Any

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from subscribe.models import PinnedPost, Subscription, SubscriptionHistory


@receiver(post_save, sender=Subscription)
def subscription_post_save(
    sender: Subscription,
    instance: Subscription,
    created: bool,
    **kwargs: dict[str, Any],
) -> None:
    """Handler of subscription creation"""
    if created:
        # Creating record in history
        SubscriptionHistory.objects.create(
            subscription=instance,
            action=SubscriptionHistory.CREATED,
            description=f"Subscription created for plan {instance.plan.name}.",
        )

    else:
        # Check if subscription status has changed
        if hasattr(instance, "_previous_status"):
            if instance._previous_status != instance.status:
                SubscriptionHistory.objects.create(
                    subscription=instance,
                    action=instance.status,
                    description=f"Subscription status changed from {instance._previous_status} to {instance.status}.",
                )


@receiver(pre_delete, sender=Subscription)
def subscription_pre_delete(
    sender: Subscription, instance: Subscription, **kwargs: dict[str, Any]
) -> None:
    """Handler of subscription deletion"""
    # Deleting pinned post in case of subscription deletion
    try:
        instance.user.pinned_post.delete()
    except PinnedPost.DoesNotExist:
        pass


@receiver(post_save, sender=PinnedPost)
def pinned_post_post_save(
    sender: PinnedPost, instance: PinnedPost, created: bool, **kwargs: dict[str, Any]
) -> None:
    """Handler of pinned post creation"""
    if created:
        # Check if user has active subscription
        if (
            not hasattr(instance.user, "subscription")
            or not instance.user.subscription.is_active
        ):
            instance.delete()
            return

        # Creating record in history
        SubscriptionHistory.objects.create(
            subscription=instance.user.subscription,
            action="post_pinned",
            description=f"Post '{instance.post.title}' pinned.",
            metadata={
                "post_id": instance.post.id,
                "post_title": instance.post.title,
            },
        )


@receiver(pre_delete, sender=PinnedPost)
def pinned_post_pre_delete(
    sender: PinnedPost, instance: PinnedPost, **kwargs: dict[str, Any]
) -> None:
    """Handler of pinned post deletion"""
    if hasattr(instance.user, "subscription"):
        # Creating record in history
        SubscriptionHistory.objects.create(
            subscription=instance.user.subscription,
            action="post_unpinned",
            description=f"Post '{instance.post.title}' unpinned.",
            metadata={
                "post_id": instance.post.id,
                "post_title": instance.post.title,
            },
        )
