from django.contrib import admin

from main.models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "created",
    )
    list_filter = ("created",)
    search_fields = ("slug", "name", "description")
    ordering = ("-created",)

    fieldsets = ((None, {"fields": ("name", "description")}),)

    readonly_fields = ("created", "slug")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "publication_status",
        "category",
        "author",
        "views_count",
        "created",
        "modified",
    )

    list_filter = (
        "category",
        "author",
        "publication_status",
        "views_count",
        "created",
        "modified",
    )
    search_fields = ("slug", "title", "category", "author")
    ordering = ("-modified", "-created")

    readonly_fields = ("created", "modified", "slug")
