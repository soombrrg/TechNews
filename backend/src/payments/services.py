import logging
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Any

import stripe
from django.conf import settings
from django.db.models import Avg, Sum
from django.utils import timezone

from payments.models import Payment, WebhookEvent
from subscribe.models import Subscription, SubscriptionHistory

logger = logging.getLogger(__name__)

# Stripe Configuration
stripe.api_key = settings.STRIPE_SECRET_KEY

if TYPE_CHECKING:
    from accounts.models import User
    from subscribe.models import SubscriptionPlan


class StripeService:
    """Service for Stripe management."""

    @staticmethod
    def create_customer(user: "User") -> str | None:
        """Create a customer in Stripe."""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.username,
                metadata={
                    "user_id": str(user.id),
                    "username": user.username,
                },
            )
            return customer.id
        except stripe.StripeError as e:
            logger.error("Error creating Stripe customer: %s", e)
            return None

    @staticmethod
    def create_checkout_session(
        payment: Payment, success_url: str, cancel_url: str
    ) -> dict[str, Any] | None:
        """Create session Stripe Checkout"""
        try:
            # Retrieving or creating user
            if payment.stripe_customer_id is None:
                customer_id = StripeService.create_customer(payment.user)
                if customer_id is None:
                    payment.mark_as_failed(
                        f"Error creating Stripe customer for: {payment.user}"
                    )
                    return None
                else:
                    payment.stripe_customer_id = customer_id
                    payment.save()

            if payment.subscription is None:
                payment.mark_as_failed(
                    "Subscription not found when creating Stripe checkout session."
                )
                return None

            session = stripe.checkout.Session.create(
                customer=payment.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": payment.currency.lower(),
                            "product_data": {
                                "name": f"Subscription - {payment.subscription.plan.name}",
                                "description": payment.description,
                            },
                            "unit_amount": int(payment.amount * 100),  # In Cents
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "payment_id": str(payment.id),
                    "user_id": str(payment.user.id),
                    "subscription_id": (
                        str(payment.subscription.id) if payment.subscription else ""
                    ),
                },
            )

            # Update payment
            payment.stripe_session_id = session.id
            payment.status = Payment.PROCESSING
            payment.save()

            return {
                "checkout_url": session.url,
                "session_id": session.id,
                "payment_id": payment.id,
            }

        except stripe.StripeError as e:
            logger.error("Error creating checkout session: %s", e)
            payment.mark_as_failed(str(e))
            return None

    @staticmethod
    def create_payment_intent(payment: Payment) -> str | None:
        """Create Stripe payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount) * 100,
                currency=payment.currency.lower(),
                metadata={
                    "payment_id": str(payment.id),
                    "user_id": str(payment.user.id),
                    "subscription_id": (
                        str(payment.subscription.id)
                        if payment.subscription
                        else None  # type:ignore
                    ),
                },
            )

            payment.stripe_payment_intent_id = intent.id
            payment.save()

            return intent.client_secret
        except stripe.StripeError as e:
            logger.error("Error creating payment intent: %s", e)
            payment.mark_as_failed(str(e))
            return None

    @staticmethod
    def refund_payment(
        payment: Payment, amount: Decimal | None = None, reason: str = ""
    ) -> bool:
        """Returns Payment through Stripe"""
        try:
            if not payment.stripe_payment_intent_id:
                return False

            refund_data = {
                "payment_intent": payment.stripe_payment_intent_id,
                "metadata": {
                    "payment_id": payment.id,
                    "reason": reason,
                },
            }

            if amount:
                refund_data["amount"] = str(int(amount * 100))

            refund = stripe.Refund.create(**refund_data)  # type: ignore

            return refund.status == Payment.SUCCEEDED
        except stripe.StripeError as e:
            logger.error("Error processing refund: %s", e)
            return False

    @staticmethod
    def retrieve_session(session_id: str) -> dict[str, Any] | None:
        """Retrieve info about Stripe session"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                "status": session.status,
                "payment_intent": session.payment_intent,
                "customer": session.customer,
                "metadata": session.metadata,
            }

        except stripe.StripeError as e:
            logger.error("Error retrieving Stripe session: %s", e)
            return None


class PaymentService:
    """Main service for payment management."""

    @staticmethod
    def create_subscription_payment(
        user: "User", plan: "SubscriptionPlan"
    ) -> tuple[Payment, Subscription]:
        """Create payment for subscription"""
        # Creating Subscription
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            status=Subscription.PENDING,
            start_date=timezone.now(),
            end_date=timezone.now(),  # Will be updated after payment
        )

        # Creating Payment
        payment = Payment.objects.create(
            user=user,
            subscription=subscription,
            amount=plan.price,
            currency="USD",
            description=f"Subscription to {plan.name}",
            payment_method=Payment.STRIPE,
        )

        # Creating record in history
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action=SubscriptionHistory.CREATED,
            description=f"Subscription created for plan {plan.name}",
        )

        return payment, subscription

    @staticmethod
    def process_successful_payment(payment: Payment) -> bool:
        """Process successful payment"""
        try:
            payment.mark_as_succeeded()

            # Activating subscription
            if payment.subscription:
                payment.subscription.activate()

                # Creating record in history
                SubscriptionHistory.objects.create(
                    subscription=payment.subscription,
                    action=SubscriptionHistory.ACTIVATED,
                    description="Subscription activated after successful payment",
                    metadata={"payment_id": payment.id},
                )
            logger.info("Payment %s processed successfully.", payment.id)
            return True

        except Exception as e:
            logger.error("Error processing successful payment %s: %s", payment.id, e)
            return False

    @staticmethod
    def process_failed_payment(payment: Payment, reason: str = "") -> bool:
        """Process failed payment"""
        try:
            payment.mark_as_failed(reason)

            # Canceling subscription
            if payment.subscription:
                payment.subscription.cancel()

                # Creating record in history
                SubscriptionHistory.objects.create(
                    subscription=payment.subscription,
                    action="payment_failed",
                    description=f"Payment failed: {reason}",
                    metadata={"payment_id": payment.id},
                )

            logger.info("Payment %s marked as failed.", payment.id)
            return True
        except Exception as e:
            logger.error("Error processing failed payment %s: %s", payment.id, e)
            return False

    @staticmethod
    def cancel_subscription(subscription: Subscription) -> bool:
        """Cancel subscription"""
        try:
            subscription.cancel()

            # Deleting pinned post if exists
            if hasattr(subscription.user, "pinned_post"):
                subscription.user.pinned_post.delete()

            # Creating record in history
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action=SubscriptionHistory.CANCELLED,
                description="Subscription cancelled by user.",
            )

            logger.info("Subscription %s cancelled.", subscription.id)
            return True
        except Exception as e:
            logger.error("Error cancelling subscription %s: %s", subscription.id, e)
            return False

    @staticmethod
    def get_payment_analytics() -> dict[str, Any]:
        """Get payment analytics"""
        # General statistic
        total_payments = Payment.objects.count()
        successful_payments = Payment.objects.filter(status=Payment.SUCCEEDED).count()
        total_revenue = (
            Payment.objects.filter(status=Payment.SUCCEEDED).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        # Statistic of last month
        current_datetime = timezone.now()
        last_month = current_datetime - timedelta(days=30)
        monthly_payments = Payment.objects.filter(
            created__gte=last_month,
            status=Payment.SUCCEEDED,
        )
        monthly_revenue = monthly_payments.aggregate(total=Sum("amount"))["total"] or 0
        monthly_count = monthly_payments.count()

        # Average payment
        avg_payment = (
            Payment.objects.filter(status=Payment.SUCCEEDED).aggregate(
                avg=Avg("amount")
            )["avg"]
            or 0
        )

        # Statistic by subscription
        active_subscriptions = Payment.objects.filter(
            status=Payment.SUCCEEDED,
            subscription__status=Subscription.ACTIVE,
        ).count()

        return {
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "success_rate": (
                round(successful_payments / total_payments * 100, 2)
                if total_payments
                else 0
            ),
            "total_revenue": round(float(total_revenue), 2),
            "monthly_revenue": round(float(monthly_revenue), 2),
            "monthly_payments": monthly_count,
            "avg_payment": round(float(avg_payment), 2),
            "active_subscriptions": active_subscriptions,
            "period": {
                "from": last_month.isoformat(),
                "to": current_datetime.isoformat(),
            },
        }


class WebhookService:
    """Service for webhook events management"""

    @staticmethod
    def process_stripe_webhook(event_data: dict[str, Any]) -> bool:
        """Processes webhook event"""
        try:
            event_id = event_data.get("id")
            event_type = event_data.get("type")

            # Check if not already processed
            if WebhookEvent.objects.filter(event_id=event_id).exists():
                return True

            if event_id is None or event_type is None:
                raise Exception("event_id or event_type not provided.")

            # Creating event record
            webhook_event = WebhookEvent.objects.create(
                provider=WebhookEvent.STRIPE,
                event_id=event_id,
                event_type=event_type,
                data=event_data,
            )

            # Handling different type of Events
            success = False

            if event_type == "checkout.session.completed":
                success = WebhookService._handle_checkout_completed(event_data)
            elif event_type == "payment_intent.succeeded":
                success = WebhookService._handle_payment_succeeded(event_data)
            elif event_type == "payment_intent.payment_failed":
                success = WebhookService._handle_payment_failed(event_data)
            elif event_type == "charge.dispute.created":
                success = WebhookService._handle_dispute_created(event_data)
            else:
                # Unknown event type - mark as ignored
                webhook_event.status = WebhookEvent.IGNORED
                webhook_event.save()
                return True

            if success:
                webhook_event.mark_as_processed()
            else:
                webhook_event.mark_as_failed("Processing failed")

            return success

        except Exception as e:
            logger.error("Error processing webhook event: %s", e)
            return False

    @staticmethod
    def _handle_checkout_completed(event_data: dict[str, Any]) -> bool:
        """Handle ending of checkout session"""
        try:
            session = event_data["data"]["object"]
            metadata = event_data.get("metadata", {})
            payment_id = event_data.get("payment_id")

            if not payment_id:
                logger.warning("No payment_id in checkout session metadata.")
                return False

            payment = Payment.objects.get(id=payment_id)
            return PaymentService.process_successful_payment(payment)

        except Payment.DoesNotExist:
            logger.error("Payment not found for checkout session.")
            return False
        except Exception as e:
            logger.error("Error handling checkout completed: %s", e)
            return False

    @staticmethod
    def _handle_payment_succeeded(event_data: dict[str, Any]) -> bool:
        """Handle successful payment"""
        try:
            payment_intent = event_data["data"]["object"]
            metadata = event_data.get("metadata", {})
            payment_id = event_data.get("payment_id")

            if not payment_id:
                logger.warning("No payment_id in payment intent metadata.")
                return False

            payment = Payment.objects.get(id=payment_id)
            payment.stripe_payment_intent_id = payment_intent["id"]
            payment.save()

            return PaymentService.process_successful_payment(payment)

        except Payment.DoesNotExist:
            logger.error("Payment not found for payment intent.")
            return False
        except Exception as e:
            logger.error("Error handling payment succeeded: %s", e)
            return False

    @staticmethod
    def _handle_payment_failed(event_data: dict[str, Any]) -> bool:
        """Handle failed payment"""
        try:
            payment_intent = event_data["data"]["object"]
            metadata = event_data.get("metadata", {})
            payment_id = event_data.get("payment_id")

            if not payment_id:
                logger.warning("No payment_id in payment intent metadata.")
                return False

            payment = Payment.objects.get(id=payment_id)

            last_error = payment_intent.get("last_payment_error", {})
            error_message = last_error.get("message", "Payment failed")

            return PaymentService.process_failed_payment(payment, error_message)

        except Payment.DoesNotExist:
            logger.error("Payment not found for payment intent.")
            return False
        except Exception as e:
            logger.error("Error handling payment failed: %s", e)
            return False

    @staticmethod
    def _handle_dispute_created(event_data: dict[str, Any]) -> bool:
        """Handle dispute creation"""
        try:
            dispute = event_data["data"]["object"]
            charge_id = dispute.get("charge_id")

            logger.info("Dispute created for charge %s", charge_id)
            return True

        except Exception as e:
            logger.error("Error handling dispute created: %s", e)
            return False
