from django.contrib import admin
from django.db.models import QuerySet
from django.http.request import HttpRequest

from comments.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post_title",
        "author",
        "content_preview",
        "parent_comment",
        "is_active",
        "created",
    )
    list_filter = ("is_active", "created", "modified")
    search_fields = ("content", "author__username", "post__title")
    readonly_fields = ("created", "modified")
    raw_id_fields = ("author", "post", "parent")
    list_editable = ("is_active",)

    fieldsets = (
        (None, {"fields": ("post", "author", "parent", "content")}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created", "modified"), "classes": ("collapse",)}),
    )

    @admin.display(description="Post")
    def post_title(self, obj: Comment) -> str:
        return obj.post.title

    @admin.display(description="Content Preview")
    def content_preview(self, obj: Comment) -> str:
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    @admin.display(description="Parent")
    def parent_comment(self, obj: Comment) -> str:
        if obj.parent:
            return f"Reply to: {obj.parent.content[:30]}..."
        return "Main comment"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Comment]:
        return super().get_queryset(request).select_related("author", "post", "parent")

    actions = ["make_active", "make_inactive"]

    @admin.display(description="Mark selected comments as active")
    def make_active(self, request: HttpRequest, queryset: QuerySet[Comment]) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} comments were marked as active.")

    @admin.display(description="Mark selected comments as inactive")
    def make_inactive(self, request: HttpRequest, queryset: QuerySet[Comment]) -> None:
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} comments were marked as inactive.")
