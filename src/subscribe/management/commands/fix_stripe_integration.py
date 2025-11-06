from typing import TYPE_CHECKING, Any

import stripe
from django.conf import settings
from django.core.management.base import BaseCommand

from subscribe.models import SubscriptionPlan

stripe.api_key = settings.STRIPE_SECRET_KEY

if TYPE_CHECKING:
    from django.core.management.base import CommandParser


class Command(BaseCommand):
    help = "Fix Stripe integration by creating real products and prices"

    def add_arguments(self, parser: "CommandParser") -> None:
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreate even if stripe_price_id exists",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        force = options["force"]

        # Check Stripe connection
        try:
            stripe.Balance.retrieve()
            self.stdout.write(self.style.SUCCESS("✅ Successful connection to Stripe"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection to Stripe error: {e}"))
            return

        # Handling all plans
        plans = SubscriptionPlan.objects.filter(is_active=True)

        for plan in plans:
            self.stdout.write(f"Handling plan: {plan.name}")

            # Check if plan need to be created
            if (
                plan.stripe_price_id
                and not force
                and plan.stripe_price_id.startswith("price_1")
            ):
                self.stdout.write(
                    f"  ⏭️ Plan already have Stripe ID: {plan.stripe_price_id}"
                )
                continue

            try:
                # Create or update Stripe Product
                product = stripe.Product.create(
                    name=plan.name,
                    description=f"Subscription plan: {plan.name}",
                    metadata={
                        "plan_id": str(plan.id),
                        "django_model": "SubscriptionPlan",
                        "created_by": "django_management_command",
                    },
                )
                self.stdout.write(f"  ✅ Product created: {product.id}")

                # Creating Price
                price = stripe.Price.create(
                    product=product.id,
                    unit_amount=int(plan.price * 100),  # In Cents
                    currency="usd",
                    recurring={"interval": "month"},
                    metadata={
                        "plan_id": str(plan.id),
                        "django_model": "SubscriptionPlan",
                    },
                )
                self.stdout.write(f"  ✅ Price created: {price.id}")

                # Updating plan
                old_id = plan.stripe_price_id
                plan.stripe_price_id = price.id
                plan.save()

                self.stdout.write(
                    self.style.SUCCESS(f"  ✅ Plan updated: {old_id} → {price.id}")
                )

            except stripe.StripeError as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Stripe error for plan {plan.name}: {e}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ General error for plan {plan.name}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS("🎉 Handling complete! Check Stripe Dashboard.")
        )
