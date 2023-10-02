"""
URLs for forum_email_notifier.
"""
from django.urls import re_path  # pylint: disable=unused-import

from platform_plugin_forum_email_notifier.api.views import (  # pylint: disable=unused-import
    ForumEmailNotificationPreferenceAPIView,
)

urlpatterns = [
    re_path(
        r"^forum_email_notification_preference",
        ForumEmailNotificationPreferenceAPIView.as_view(),
        name="forum_email_notification_preference",
    ),
]
