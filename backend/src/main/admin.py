from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from main.models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "posts_count", "created")
    list_filter = ("created",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created", "posts_count")

    @admin.display(description="Posts Count")
    def posts_count(self, obj: Category) -> int:
        return obj.posts.count()

    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "posts_count", "created")}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "publication_status",
        "views_count",
        "comments_count",
        "created",
    )
    list_filter = (
        "publication_status",
        "category",
        "created",
        "modified",
    )
    search_fields = ("title", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created", "modified", "views_count", "comments_count")
    raw_id_fields = ("author",)

    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "image")}),
        ("Meta", {"fields": ("category", "author", "publication_status")}),
        (
            "Statistics",
            {
                "fields": ("views_count", "comments_count", "created", "modified"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="Comments Count")
    def comments_count(self, obj: Post) -> int:
        return obj.comments.count()

    def get_queryset(self, request: HttpRequest) -> QuerySet[Post]:
        return super().get_queryset(request).select_related("author", "category")
