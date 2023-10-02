"""
forum_email_notifier Django application initialization.
"""

from django.apps import AppConfig
from openedx.core.constants import COURSE_ID_PATTERN


class PlatformPluginForumEmailNotifierConfig(AppConfig):
    """
    Configuration for the forum_email_notifier Django application.
    """

    name = "platform_plugin_forum_email_notifier"
    verbose_name = "Forum Email Notifier"

    plugin_app = {
        "url_config": {
            "lms.djangoapp": {
                "namespace": "platform_plugin_forum_email_notifier",
                "regex": rf"courses/{COURSE_ID_PATTERN}/instructor/api/",
                "relative_path": "urls",
            }
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
                "test": {"relative_path": "settings.test"},
                "production": {"relative_path": "settings.production"},
            },
        },
    }

    def ready(self):
        super().ready()

        from platform_plugin_forum_email_notifier import (  # pylint: disable=unused-import, import-outside-toplevel
            admin,
            email,
            handlers,
            tasks,
        )
        from platform_plugin_forum_email_notifier.extensions import filters
