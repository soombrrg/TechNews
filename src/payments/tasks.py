from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from payments.models import Payment, WebhookEvent


@shared_task
def cleanup_old_payments() -> dict[str, int]:
    """Cleanup old payments"""
    cutoff_date = timezone.now() - timedelta(days=90)

    # Deleting old failed/ cancelled Payments
    old_payments = Payment.objects.filter(
        created__lt=cutoff_date,
        status__in=[
            Payment.CANCELLED,
            Payment.FAILED,
        ],
    )

    deleted_payments, _ = old_payments.delete()

    return {"deleted_payments": deleted_payments}


@shared_task
def cleanup_old_webhook_events() -> dict[str, int]:
    """Cleanup old webhook events"""
    cutoff_date = timezone.now() - timedelta(days=30)

    # Deleting old handled events
    old_events = WebhookEvent.objects.filter(
        created__lt=cutoff_date,
        status__in=[
            WebhookEvent.PROCESSED,
            WebhookEvent.IGNORED,
        ],
    )

    deleted_events, _ = old_events.delete()

    return {"deleted_webhook_events": deleted_events}


@shared_task
def retry_failed_webhook_events() -> dict[str, int]:
    """Retry failed webhook events handling"""
    from payments.services import WebhookService

    # Finding events, that was not handled in last 24 hours
    retry_cutoff = timezone.now() - timedelta(hours=24)

    # Limiting amount for re-handling
    failed_events = WebhookEvent.objects.filter(
        status=WebhookEvent.FAILED,
        created__lt=retry_cutoff,
    )[:50]

    processed_count = 0

    for event in failed_events:
        success = WebhookService.process_stripe_webhook(event.data)
        if success:
            event.mark_as_processed()
            processed_count += 1

    return {"re_processed_count": processed_count}
