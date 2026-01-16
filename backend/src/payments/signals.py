from typing import Any

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from payments.models import Payment
from payments.services import PaymentService


@receiver(pre_save, sender=Payment)
def payment_pre_save(
    sender: Payment, instance: Payment, *args: Any, **kwargs: dict[str, Any]
) -> None:
    """Handles previous_status for tracking Payment changes"""
    if instance.pk:
        try:
            previous = Payment.objects.get(pk=instance.pk)
            instance.previous_status = previous.status
        except Payment.DoesNotExist:
            instance._previous_status = None


@receiver(post_save, sender=Payment)
def payment_post_save(
    sender: Payment, instance: Payment, created: bool, **kwargs: dict[str, Any]
) -> None:
    """Handles payment status changing"""
    if not created and hasattr(instance, "_previous_status"):
        if instance._previous_status in [Payment.PENDING, Payment.PROCESSING]:
            # If status changed to succeeded
            if instance.status == Payment.SUCCEEDED:
                PaymentService.process_successful_payment(instance)
            # Status changed to failed
            elif instance.status == Payment.FAILED:
                PaymentService.process_failed_payment(instance)
