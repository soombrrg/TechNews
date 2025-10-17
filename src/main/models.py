from django.db import models
from django.urls import reverse

from app.models import AuthoredModel, PublishedModel, SluggedModel, TimeStampedModel


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

    def __str__(self):
        return self.name

    @property
    def slug_source(self) -> str:
        return self.name


class Post(AuthoredModel, SluggedModel, PublishedModel, TimeStampedModel):
    """Model for Posts"""

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(app_label)s_%(class)s_posts",
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)

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

    def __str__(self):
        return self.title

    @property
    def slug_source(self) -> str:
        return self.title

    @property
    def comments_count(self) -> int:
        """Count of comments for post"""
        try:
            return self.comments.filter(is_acitve=True).count()
        except AttributeError:
            return 0

    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"slug": self.slug})

    def increment_views(self):
        """Increment the views count"""
        self.views_count += 1
        self.save(update_fields=["views_counts"])
