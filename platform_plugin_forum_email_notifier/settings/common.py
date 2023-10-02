"""
Common Django settings for eox_hooks project.
For more information on this file, see
https://docs.djangoproject.com/en/2.22/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.22/ref/settings/
"""
from platform_plugin_forum_email_notifier import ROOT_DIRECTORY

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.22/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "secret-key"


# Application definition

INSTALLED_APPS = []


# Internationalization
# https://docs.djangoproject.com/en/2.22/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_TZ = True


def plugin_settings(settings):
    """
    Set of plugin settings used by the Open Edx platform.
    More info: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/plugins/README.rst
    """
    settings.MAKO_TEMPLATE_DIRS_BASE.append(ROOT_DIRECTORY / "templates")
