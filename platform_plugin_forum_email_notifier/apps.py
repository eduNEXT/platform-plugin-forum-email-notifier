"""
forum_email_notifier Django application initialization.
"""

from django.apps import AppConfig


class PlatformPluginForumEmailNotifierConfig(AppConfig):
    """
    Configuration for the forum_email_notifier Django application.
    """

    name = "platform_plugin_forum_email_notifier"

    plugin_app = {
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

        from platform_plugin_forum_email_notifier.signals import forum_thread_created_handler
