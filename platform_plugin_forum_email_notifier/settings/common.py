"""
Common Django settings for eox_hooks project.
For more information on this file, see
https://docs.djangoproject.com/en/2.22/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.22/ref/settings/
"""

from os.path import abspath, dirname, join

from platform_plugin_forum_email_notifier import ROOT_DIRECTORY

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.22/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "secret-key"


# Application definition

INSTALLED_APPS = [
    "platform_plugin_forum_email_notifier",
]


# Internationalization
# https://docs.djangoproject.com/en/2.22/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_TZ = True


def here(*x):
    return join(abspath(dirname(__file__)), *x)


PROJECT_ROOT = here("..")


def root(*x):
    return join(abspath(PROJECT_ROOT), *x)


# TEMPLATE CONFIGURATION
# See: https://docs.djangoproject.com/en/1.8/ref/settings/#templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": (root("templates"),),
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "credentials.apps.core.context_processors.core",
            ),
            "debug": True,  # Django will only display debug pages if the global DEBUG setting is set to True.
        },
    },
]


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates")
    settings.FORUM_NOTIFIER_URL = "api/forum_email_notification_preference"
    settings.FORUM_NOTIFIER_COURSE_OVERVIEWS_BACKEND = (
        "platform_plugin_forum_email_notifier.edxapp_wrapper.backends.course_overviews_p_v1"
    )
    settings.FORUM_NOTIFIER_LANG_PREF_BACKEND = (
        "platform_plugin_forum_email_notifier.edxapp_wrapper.backends.lang_pref_p_v1"
    )
    settings.FORUM_NOTIFIER_USER_API_BACKEND = (
        "platform_plugin_forum_email_notifier.edxapp_wrapper.backends.user_api_p_v1"
    )
