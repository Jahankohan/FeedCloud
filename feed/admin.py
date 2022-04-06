from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from feed.models import Feed, FollowFeed, Entry, EntryRead


class FollowFeedAdminInline(admin.TabularInline):
    model = FollowFeed
    verbose_name = "Followed Feed"
    verbose_name_plural = "Followed Feeds"
    fields = (
        "user",
        "created_at",
    )
    readonly_fields = (
        "user",
        "created_at",
    )
    can_delete = False
    classes = ["collapse"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    model = Feed
    fields = (
        "id",
        "creator",
        "title",
        "link",
        "timeout",
        "status",
        "priority",
        "created_at",
        "updated_at",
    )
    list_display = (
        "id",
        "title",
        "link",
        "timeout",
        "status",
        "priority",
    )
    list_filter = (
        "timeout",
        "status",
        "priority",
    )
    search_fields = (
        "title",
        "link",
        "creator__username",
    )
    readonly_fields = (
        "id",
        "creator",
        "link",
        "created_at",
        "updated_at",
    )
    list_max_show_all = 100
    list_per_page = 100
    inlines = (FollowFeedAdminInline,)

    def creator_link(self, obj):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:authnz_user_change", args=(obj.creator.pk,)),
                obj.creator.email,
            )
        )

    creator_link.short_description = "creator"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class EntryReadAdminInline(admin.TabularInline):
    model = EntryRead
    fields = (
        "user",
        "created_at",
    )
    readonly_fields = (
        "user",
        "created_at",
    )
    can_delete = False
    classes = ["collapse"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    model = Entry
    fields = (
        "id",
        "feed",
        "title",
        "link",
        "summary",
        "created_at",
        "published_at",
    )
    list_display = (
        "id",
        "feed",
        "title",
        "link",
        "summary",
    )
    search_fields = ("title", "link", "summary", "feed__title")
    readonly_fields = (
        "id",
        "feed",
        "title",
        "link",
        "summary",
        "created_at",
        "published_at",
    )
    list_max_show_all = 100
    list_per_page = 100
    inlines = (EntryReadAdminInline,)

    def feed_link(self, obj):
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse("admin:feed_feed_change", args=(obj.feed.pk,)), obj.feed.title
            )
        )

    feed_link.short_description = "feed"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
