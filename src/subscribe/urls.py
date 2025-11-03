from django.urls import path

from subscribe.api.views import (
    PinnedPostView,
    SubscriptionHistoryView,
    SubscriptionPlanDetailView,
    SubscriptionPlanListView,
    UserSubscriptionView,
    can_pin_post,
    cancel_subscription,
    pinned_posts_list,
    subscription_status,
)

app_name = "subscribe"

urlpatterns = [
    # Subscription plans
    path("plans/", SubscriptionPlanListView.as_view(), name="subscription-plan-list"),
    path(
        "plans/<int:pk>/",
        SubscriptionPlanDetailView.as_view(),
        name="subscription-plan-detail",
    ),
    # User subscription
    path("my-subscription/", UserSubscriptionView.as_view(), name="my-subscription"),
    path("status/", subscription_status, name="subscription-status"),
    path("history/", SubscriptionHistoryView.as_view(), name="subscription-history"),
    path("cancel/", cancel_subscription, name="cancel-subscription"),
    # Pinned posts
    path("my-pinned-post/", PinnedPostView.as_view(), name="my-pinned-post"),
    path("pinned-posts/", pinned_posts_list, name="pinned-posts-list"),
    path("can-pin/<int:post_id>/", can_pin_post, name="can-pin-post"),
]
