from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from payments.models import Payment, PaymentAttempt, Refund, WebhookEvent


class PaymentAttemptInline(admin.TabularInline):
    model = PaymentAttempt
    extra = 0
    readonly_fields = (
        "stripe_charge_id",
        "status",
        "error_message",
        "metadata",
        "created",
    )
    can_delete = False

    def has_add_permission(self, request: HttpRequest, obj: None = None) -> bool:
        return False


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    readonly_fields = (
        "amount",
        "status",
        "stripe_refund_id",
        "created",
        "processed_at",
    )
    fields = ("amount", "reason", "status", "created_by")
    can_delete = False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_link",
        "amount_display",
        "status_display",
        "payment_method",
        "subscription_link",
        "created",
    )
    list_filter = ("status", "payment_method", "currency", "created")
    search_fields = (
        "user__username",
        "user__email",
        "stripe_payment_intent_id",
        "stripe_session_id",
        "description",
    )
    readonly_fields = (
        "created",
        "modified",
        "processed_at",
        "is_successful",
        "is_pending",
        "can_be_refunded",
    )
    raw_id_fields = ("user", "subscription")
    inlines = [PaymentAttemptInline, RefundInline]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "subscription",
                    "amount",
                    "currency",
                    "status",
                    "payment_method",
                )
            },
        ),
        ("Description", {"fields": ("description",)}),
        (
            "Stripe Data",
            {
                "fields": (
                    "stripe_payment_intent_id",
                    "stripe_session_id",
                    "stripe_customer_id",
                ),
                "classes": ("collapse",),
            },
        ),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
        (
            "Status Info",
            {
                "fields": ("is_successful", "is_pending", "can_be_refunded"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created", "modified", "processed_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="User")
    def user_link(self, obj: Payment) -> str:
        """Link to user"""
        url = reverse("admin:accounts_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    @admin.display(description="Subscription")
    def subscription_link(self, obj: Payment) -> str:
        """Link to subscription"""
        if obj.subscription:
            url = reverse(
                "admin:subscribe_subscription_change", args=[obj.subscription.pk]
            )
            return format_html('<a href="{}">{}</a>', url, obj.subscription.plan.name)
        return "-"

    @admin.display(description="Amount")
    def amount_display(self, obj: Payment) -> str:
        """Displaying amount"""
        return f"${obj.amount} {obj.currency}"

    @admin.display(description="Status")
    def status_display(self, obj: Payment) -> str:
        """Displaying status in color"""
        colors = {
            obj.SUCCEEDED: "green",
            obj.FAILED: "red",
            obj.PENDING: "orange",
            obj.PROCESSING: "blue",
            obj.CANCELLED: "gray",
            obj.REFUNDED: "purple",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper(),
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Payment]:
        return (
            super()
            .get_queryset(request)
            .select_related("user", "subscription", "subscription__plan")
        )

    actions = ["mark_as_succeeded", "mark_as_failed"]

    @admin.action(description="Mark selected payments as succeeded")
    def mark_as_succeeded(
        self, request: HttpRequest, queryset: QuerySet[Payment]
    ) -> None:
        """Mark payments as succeeded"""
        count = queryset.filter(status__in=["pending", "processing"]).update(
            status="succeeded"
        )
        self.message_user(request, f"{count} payments marked as succeeded.")

    @admin.action(description="Mark selected payments as failed")
    def mark_as_failed(self, request: HttpRequest, queryset: QuerySet[Payment]) -> None:
        """Mark selected payments as failed"""
        count = queryset.filter(status__in=["pending", "processing"]).update(
            status="failed"
        )
        self.message_user(request, f"{count} payments marked as failed.")


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "payment_link",
        "stripe_charge_id",
        "status",
        "error_message_short",
        "created",
    )
    list_filter = ("status", "created")
    search_fields = ("payment__id", "stripe_charge_id", "error_message")
    readonly_fields = (
        "payment",
        "stripe_charge_id",
        "status",
        "error_message",
        "metadata",
        "created",
    )

    @admin.display(description="Payment")
    def payment_link(self, obj: PaymentAttempt) -> str:
        """Link to payment"""
        url = reverse("admin:payment_payment_change", args=[obj.payment.pk])
        return format_html('<a href="{}">Payment #{}</a>', url, obj.payment.id)

    @admin.display(description="Error")
    def error_message_short(self, obj: PaymentAttempt) -> str:
        """Short error message"""
        if obj.error_message:
            return (
                obj.error_message[:100] + "..."
                if len(obj.error_message) > 100
                else obj.error_message
            )
        return "-"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: None = None) -> bool:
        return False


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "payment_link",
        "amount_display",
        "status_display",
        "is_partial_display",
        "created_by",
        "created",
    )
    list_filter = ("status", "created")
    search_fields = ("payment__id", "stripe_refund_id", "reason")
    readonly_fields = ("created", "processed_at", "is_partial")
    raw_id_fields = ("payment", "created_by")

    fieldsets = (
        (None, {"fields": ("payment", "amount", "reason", "status")}),
        ("Stripe", {"fields": ("stripe_refund_id",), "classes": ("collapse",)}),
        ("Management", {"fields": ("created_by",)}),
        ("Status", {"fields": ("is_partial",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created", "processed_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Payment")
    def payment_link(self, obj: Refund) -> str:
        """Link to payment"""
        url = reverse("admin:payment_payment_change", args=[obj.payment.pk])
        return format_html('<a href="{}">Payment #{}</a>', url, obj.payment.id)

    @admin.display(description="Amount")
    def amount_display(self, obj: Refund) -> str:
        """Displaying amount"""
        return f"${obj.amount}"

    @admin.display(description="Status")
    def status_display(self, obj: Refund) -> str:
        """Displaying status in color"""
        colors = {
            obj.SUCCEEDED: "green",
            obj.FAILED: "red",
            obj.PENDING: "orange",
            obj.CANCELLED: "gray",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper(),
        )

    @admin.display(description="Type")
    def is_partial_display(self, obj: Refund) -> str:
        """Displaying partial refund"""
        if obj.is_partial:
            return format_html('<span style="color: orange;">Partial</span>')
        else:
            return format_html('<span style="color: green;">Full</span>')

    def get_queryset(self, request: HttpRequest) -> QuerySet[Refund]:
        return super().get_queryset(request).select_related("payment", "created_by")


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "provider",
        "event_type",
        "status_display",
        "error_message_short",
        "created",
    )
    list_filter = ("provider", "status", "event_type", "created")
    search_fields = ("event_id", "event_type", "error_message")
    readonly_fields = (
        "provider",
        "event_id",
        "event_type",
        "data",
        "created",
        "processed_at",
    )

    fieldsets = (
        (None, {"fields": ("provider", "event_id", "event_type", "status")}),
        ("Processing", {"fields": ("error_message",)}),
        ("Data", {"fields": ("data",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created", "processed_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Status")
    def status_display(self, obj: WebhookEvent) -> str:
        """Displaying status in color"""
        colors = {
            obj.PROCESSED: "green",
            obj.FAILED: "red",
            obj.PENDING: "orange",
            obj.IGNORED: "gray",
        }
        color = colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status.upper(),
        )

    @admin.display(description="Error")
    def error_message_short(self, obj: WebhookEvent) -> str:
        """Short error message"""
        if obj.error_message:
            return (
                obj.error_message[:100] + "..."
                if len(obj.error_message) > 100
                else obj.error_message
            )
        return "-"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: None = None) -> bool:
        # Enabling deleting only for old events
        return request.user.is_superuser

    actions = ["mark_as_processed", "retry_failed_events"]

    @admin.action(description="Mark selected events as processed")
    def mark_as_processed(
        self, request: HttpRequest, queryset: QuerySet[WebhookEvent]
    ) -> None:
        """Mark events as processed"""
        count = queryset.filter(status="pending").update(status="processed")
        self.message_user(request, f"{count} events marked as processed.")

    @admin.action(description="Retry failed events")
    def retry_failed_events(
        self, request: HttpRequest, queryset: QuerySet[WebhookEvent]
    ) -> None:
        """Repeated handling of failed events"""
        from .services import WebhookService

        count = 0
        for event in queryset.filter(status="failed"):
            success = WebhookService.process_stripe_webhook(event.data)
            if success:
                event.mark_as_processed()
                count += 1

        self.message_user(request, f"{count} events reprocessed successfully.")
