"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from os.path import abspath, dirname, join


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'platform_plugin_forum_email_notifier',
)

LOCALE_PATHS = [
    root('platform_plugin_forum_email_notifier', 'conf', 'locale'),
]

ROOT_URLCONF = 'platform_plugin_forum_email_notifier.urls'

SECRET_KEY = 'insecure-secret-key'

MIDDLEWARE = (
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': False,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',  # this is required for admin
            'django.contrib.messages.context_processors.messages',  # this is required for admin
        ],
    },
}]

FORUM_NOTIFIER_LANG_PREF_BACKEND = (
    "platform_plugin_forum_email_notifier.edxapp_wrapper.backends.tests.lang_pref_p_v1_test"
)
FORUM_NOTIFIER_COURSE_OVERVIEWS_BACKEND = (
    "platform_plugin_forum_email_notifier.edxapp_wrapper.backends.tests.course_overviews_p_v1_test"
)
FORUM_NOTIFIER_USER_API_BACKEND = (
    "platform_plugin_forum_email_notifier.edxapp_wrapper.backends.tests.user_api_p_v1_test"
)
