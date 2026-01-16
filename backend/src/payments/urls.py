from django.urls import path

from payments.api.views import (
    PaymentDetailView,
    PaymentListView,
    RefundDetailView,
    RefundListView,
    cancel_payment,
    create_checkout_session_view,
    create_refund,
    payment_analytics,
    payment_status,
    retry_payment,
    stripe_webhook,
    user_payment_history,
)

app_name = "payments"

urlpatterns = [
    # Payments
    path("", PaymentListView.as_view(), name="payment-list"),
    path("<uuid:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("<uuid:payment_id>/status/", payment_status, name="payment-status"),
    path("<uuid:payment_id>/cancel/", cancel_payment, name="payment-cancel"),
    path("<uuid:payment_id>/retry/", retry_payment, name="payment-retry"),
    path("history/", user_payment_history, name="payment-history"),
    # Checkout
    path(
        "create-checkout-session/",
        create_checkout_session_view,
        name="create-checkout-session",
    ),
    # Refunds (Admin only)
    path("refunds/", RefundListView.as_view(), name="refund-list"),
    path("refunds/<uuid:pk>/", RefundDetailView.as_view(), name="refund-detail"),
    path("<uuid:payment_id>/refund/", create_refund, name="refund-create"),
    # Analytics (Admin only)
    path("analytics/", payment_analytics, name="payment-analytics"),
    # Webhooks
    path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
]
