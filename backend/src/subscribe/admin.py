from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from subscribe.models import (
    PinnedPost,
    Subscription,
    SubscriptionHistory,
    SubscriptionPlan,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "duration_days",
        "is_active",
        "subscriptions_count",
        "created",
    )
    list_filter = (
        "is_active",
        "created",
    )
    search_fields = ("name", "stripe_price_id")
    readonly_fields = ("created", "modified")

    fieldsets = (
        (None, {"fields": ("name", "price", "duration_days", "stripe_price_id")}),
        ("Features", {"fields": ("features",), "classes": ("collapse",)}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created", "modified"), "classes": ("collapse",)}),
    )

    @admin.display(description="Subscriptions")
    def subscriptions_count(self, obj: SubscriptionPlan) -> int:
        """Count of subscriptions"""
        return obj.subscriptions.count()

    def get_queryset(self, request: HttpRequest) -> QuerySet["SubscriptionPlan"]:
        return super().get_queryset(request).prefetch_related("subscriptions")


class SubscriptionHistoryInline(admin.TabularInline):
    model = SubscriptionHistory
    extra = 0
    readonly_fields = ("action", "description", "metadata", "created")
    can_delete = False

    def has_add_permission(self, request: HttpRequest, obj: None = None) -> bool:
        return False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user_link",
        "plan",
        "status",
        "is_active_display",
        "days_remaining_display",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "plan", "auto_renew", "created")
    search_fields = ("user__username", "user__email", "plan__name")
    readonly_fields = ("created", "modified", "is_active", "days_remaining")
    raw_id_fields = ("user",)
    inlines = (SubscriptionHistoryInline,)

    fieldsets = (
        (None, {"fields": ("user", "plan", "status")}),
        ("Dates", {"fields": ("start_date", "end_date", "auto_renew")}),
        ("Stripe", {"fields": ("stripe_subscription_id",), "classes": ("collapse",)}),
        (
            "Status",
            {"fields": ("is_active", "days_remaining"), "classes": ("collapse",)},
        ),
        ("Timestamps", {"fields": ("created", "modified"), "classes": ("collapse",)}),
    )

    @admin.display(description="User")
    def user_link(self, obj: Subscription) -> str:
        """Link to user"""
        url = reverse("admin:accounts_user_change", args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    @admin.display(description="Active")
    def is_active_display(self, obj: Subscription) -> str:
        """Display subscription activity"""
        if obj.is_active:
            return format_html('<span style="color:green;">Active</span>')
        else:
            return format_html('<span style="color:red;">Inactive</span>')

    @admin.display(description="Days Remaining")
    def days_remaining_display(self, obj: Subscription) -> str:
        """Display remaining days"""
        days = obj.days_remaining
        if days > 7:
            color = "green"
        elif days > 0:
            color = "orange"
        else:
            color = "red"

        return format_html("<span style='color:{};'>{}</span>", color, days)

    def get_queryset(self, request: HttpRequest) -> QuerySet["Subscription"]:
        return super().get_queryset(request).select_related("user", "plan")

    actions = ["activate_subscriptions", "cancel_subscriptions", "expire_subscriptions"]

    @admin.action(description="Activate selected Subscriptions")
    def activate_subscriptions(
        self, request: HttpRequest, queryset: QuerySet["Subscription"]
    ) -> None:
        """Activate subscriptions"""
        count = 0
        for subscription in queryset:
            if subscription.status != Subscription.ACTIVE:
                subscription.activate()
                count += 1

        self.message_user(request, f"{count} subscription(s) activated.")

    @admin.action(description="Cancel selected Subscriptions")
    def cancel_subscriptions(
        self, request: HttpRequest, queryset: QuerySet["Subscription"]
    ) -> None:
        """Cancel subscriptions"""
        count = 0
        for subscription in queryset:
            if subscription.status != Subscription.CANCELLED:
                subscription.cancel()
                count += 1

        self.message_user(request, f"{count} subscription(s) cancelled.")

    @admin.action(description="Expire selected Subscriptions")
    def expire_subscriptions(
        self, request: HttpRequest, queryset: QuerySet["Subscription"]
    ) -> None:
        """Expire subscriptions"""
        count = 0
        for subscription in queryset:
            if subscription.status != Subscription.CANCELLED:
                subscription.expire()
                count += 1

        self.message_user(request, f"{count} subscription(s) expired.")


@admin.register(PinnedPost)
class PinnedPostAdmin(admin.ModelAdmin):
    list_display = ("user_link", "post_link", "subscription_status", "pinned_at")
    list_filter = ("pinned_at", "user__subscription__status")
    search_fields = ("user__username", "post__title")
    readonly_fields = ("pinned_at",)
    raw_id_fields = ("user", "post")

    @admin.display(description="User")
    def user_link(self, obj: PinnedPost) -> str:
        """Link to user"""
        url = reverse("admin:accounts_user_change", args=(obj.user.pk,))
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    @admin.display(description="Post")
    def post_link(self, obj: PinnedPost) -> str:
        """Link to post"""
        url = reverse("admin:main_post_change", args=(obj.post.pk,))
        return format_html('<a href="{}">{}</a>', url, obj.post.title[:50])

    @admin.display(description="Subscription")
    def subscription_status(self, obj: PinnedPost) -> str:
        """Subscription status"""
        if hasattr(obj.user, "subscription") and obj.user.subscription.is_active:
            return format_html('<span style="color:green;">Active</span>')
        else:
            return format_html('<span style="color:red;">Inactive</span>')

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Forbidding creation through admin panel"""
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet["PinnedPost"]:
        return (
            super()
            .get_queryset(request)
            .select_related("user", "user__subscription", "post")
        )


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    list_display = ("subscription_link", "action", "description_short", "created")
    list_filter = ("action", "created")
    search_fields = ("subscription__user__username", "description")
    readonly_fields = ("subscription", "action", "description", "metadata", "created")

    @admin.display(description="Subscription")
    def subscription_link(self, obj: SubscriptionHistory) -> str:
        """Link to subscription"""
        url = reverse(
            "admin:subscribe_subscription_change", args=(obj.subscription.pk,)
        )
        return format_html(
            '<a href="{}">{} - {}</a>',
            url,
            obj.subscription.user.username,
            obj.subscription.plan.name,
        )

    @admin.display(description="Description")
    def description_short(self, obj: SubscriptionHistory) -> str:
        """Short description"""
        return (
            obj.description[:100] + "..."
            if len(obj.description) > 100
            else obj.description
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Forbidding creation through admin panel"""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: None = None) -> bool:
        """Forbidding deleting through admin panel"""
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet["SubscriptionHistory"]:
        return (
            super()
            .get_queryset(request)
            .select_related("subscription", "subscription__user", "subscription__plan")
        )


# Additional admin panel configurations
admin.site.site_header = "TechNews Administration"
admin.site.site_title = "TechNews Admin"
admin.site.index_title = "Welcome to TechNews Administration"
