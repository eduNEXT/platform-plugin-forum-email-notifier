"""
Language Preferences module generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def get_language_key():
    """
    Wrapper for `LANGUAGE_KEY` function in edx-platform.
    """
    backend_function = settings.FORUM_NOTIFIER_LANG_PREF_BACKEND
    backend = import_module(backend_function)

    return backend.LANGUAGE_KEY


LANGUAGE_KEY = get_language_key()
