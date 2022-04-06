from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authnz.models import User
from feed.models import FollowFeed, EntryRead


class FollowFeedAdminInline(admin.TabularInline):
    model = FollowFeed
    verbose_name = "Followed Feed"
    verbose_name_plural = "Followed Feeds"
    fields = (
        "feed",
        "created_at",
    )
    readonly_fields = (
        "feed",
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


class EntryReadAdminInline(admin.TabularInline):
    model = EntryRead
    fields = (
        "entry",
        "created_at",
    )
    readonly_fields = (
        "entry",
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


class UserAdmin(UserAdmin):
    list_filter = UserAdmin.list_filter + ("email_confirmed",)
    list_display = UserAdmin.list_display + ("email_confirmed",)
    fieldsets = UserAdmin.fieldsets
    fieldsets[1][1]["fields"] = UserAdmin.fieldsets[1][1]["fields"] + (
        "email_confirmed",
    )
    inlines = (
        FollowFeedAdminInline,
        EntryReadAdminInline,
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.email_confirmed:
            self.readonly_fields += ("email_confirmed",)
        return self.readonly_fields


admin.site.register(User, UserAdmin)
