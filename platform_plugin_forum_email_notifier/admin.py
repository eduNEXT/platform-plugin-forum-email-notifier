"""Admin module for the forum email notifier project."""
from django.contrib import admin

from platform_plugin_forum_email_notifier.models import ForumNotificationDigest, ForumNotificationPreference


@admin.register(ForumNotificationPreference)
class ForumNotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for the ForumNotificationPreference model."""

    list_display = (
        "user",
        "preference",
        "course_id",
    )
    search_fields = ("user", "course_id")

    class Meta:
        """Meta class for ForumNotificationPreferenceAdmin."""

        model = ForumNotificationPreference


@admin.register(ForumNotificationDigest)
class ForumNotificationDigestAdmin(admin.ModelAdmin):
    """Admin interface for the ForumNotificationDigest model."""

    list_display = (
        "user",
        "digest_type",
        "course_id",
    )
    search_fields = ("user", "course_id")

    class Meta:
        """Meta class for ForumNotificationDigestAdmin."""

        model = ForumNotificationPreference
