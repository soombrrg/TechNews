from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.db.models.functions import Now
from django.urls import reverse

from app.models import PublishedModel, SluggedModel, TimeStampedModel

if TYPE_CHECKING:
    from accounts.models import User


class Category(SluggedModel):
    """Model for Posts Categories"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.name

    @property
    def slug_source(self) -> str:
        return self.name


class PinnedPostQuerySet(models.QuerySet["Post"]):
    """QuerySet for Post Model"""

    def pinned(self) -> QuerySet["Post"]:
        """Returns a queryset of pinned posts in pinned_at order"""
        from subscribe.models import Subscription  # noqa

        return (
            self.filter(
                pin_info__isnull=False,
                pin_info__user__subscription__status=Subscription.ACTIVE,
                pin_info__user__subscription__end_date__gt=Now(),
                publication_status=PublishedModel.PUBLISHED,
            )
            .select_related(
                "pin_info",
                "pin_info__user",
                "pin_info__user__subscription",
            )
            .order_by("pinned_at")
        )

    def regular_posts(self) -> QuerySet["Post"]:
        """Returns a queryset of regular (unpinned) posts"""
        return self.filter(
            pin_info__isnull=True, publication_status=PublishedModel.PUBLISHED
        )

    def with_subscription_info(self) -> QuerySet["Post"]:
        """Returns a queryset of posts with info about author subscription"""
        return self.select_related(
            "author",
            "author__subscription",
            "category",
        ).prefetch_related("pin_info")


class Post(SluggedModel, PublishedModel, TimeStampedModel):
    """Model for Posts with pinning possibility"""

    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)

    objects = PinnedPostQuerySet.as_manager()  # type: ignore

    class Meta:
        db_table = "posts"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
            models.Index(fields=["publication_status", "-created"]),
            models.Index(fields=["category", "-created"]),
            models.Index(fields=["author", "-created"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("post-detail", kwargs={"slug": self.slug})

    @property
    def slug_source(self) -> str:
        return self.title

    @property
    def comments_count(self) -> int:
        """Count of comments for post"""
        try:
            return self.comments.filter(is_active=True).count()
        except AttributeError:
            return 0

    @property
    def is_pinned(self) -> bool:
        """Check if post is pinned"""
        return hasattr(self, "pin_info") and self.pin_info is not None

    @property
    def is_published(self) -> bool:
        """Check if post can be pinned by user"""
        if self.publication_status != self.PUBLISHED:
            return False
        return True

    def can_be_pinned_by(self, user: "User") -> bool:
        """Check if post can be pinned by user"""
        if not user or not user.is_authenticated:
            return False

        # Post should be authored by user
        if self.author != user:
            return False

        # Post should be published
        if not self.is_published:
            return False

        # User must have active subscription
        if not hasattr(user, "subscription") or not user.subscription.is_active:
            return False

        return True

    def get_pinned_info(self) -> dict[str, Any]:
        """Return pinned post info"""
        if self.is_pinned:
            return {
                "is_pinned": True,
                "pinned_at": self.pin_info.pinned_at,
                "pinned_by": {
                    "id": self.pin_info.user.id,
                    "username": self.pin_info.user.username,
                    "has_active_subscription": self.pin_info.user.subscription.is_active,
                },
            }
        return {"is_pinned": False}

    def increment_views(self) -> None:
        """Increment the views count"""
        self.views_count += 1
        self.save(update_fields=["views_count"])
