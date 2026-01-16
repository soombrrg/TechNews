from django.conf import settings
from django.db import models
from django.db.models import Count, Prefetch, Q

from app.models import TimeStampedModel


class CommentQuerySet(models.QuerySet["Comment"]):
    def with_replies_count(self) -> "CommentQuerySet":
        return self.annotate(
            replies_count=Count(
                "replies",
                filter=Q(replies__is_active=True),
            )
        )

    def with_replies(self) -> "CommentQuerySet":
        return self.prefetch_related(
            Prefetch(
                "replies",
                queryset=Comment.objects.filter(is_active=True)
                .select_related("author")
                .with_replies_count()
                .order_by("-created"),
            )
        )


class Comment(TimeStampedModel):
    """Model for comments"""

    post = models.ForeignKey(
        "main.Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
    )

    content = models.TextField()
    is_active = models.BooleanField(default=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        db_table = "comments"
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ("-created",)
        indexes = [
            models.Index(fields=["post", "-created"]),
            models.Index(fields=["author", "-created"]),
            models.Index(fields=["parent", "-created"]),
        ]

    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.post.title}"

    @property
    def is_reply(self) -> bool:
        return self.parent is not None
