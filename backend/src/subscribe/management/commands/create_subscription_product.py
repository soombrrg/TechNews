from typing import Any

from django.core.management.base import BaseCommand

from subscribe.models import SubscriptionPlan


class Command(BaseCommand):
    help = "Create default subscription plans"

    def handle(self, *args: Any, **options: Any) -> None:
        # Creating base subscription plan
        plan, created = SubscriptionPlan.objects.get_or_create(
            name="Premium Monthly",
            defaults={
                "price": 12.00,
                "duration_days": 30,
                "stripe_price_id": "price_premium_monthly",  # Replace with real ID from Stripe
                "features": {
                    "pin_posts": True,
                    "priority_support": True,
                    "analytics": True,
                },
                "is_active": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Created subscription plan: {plan.name}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Subscription plan already exists: {plan.name}")
            )
