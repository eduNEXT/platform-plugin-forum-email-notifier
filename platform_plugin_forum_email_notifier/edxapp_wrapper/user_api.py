"""
Course Overviews module generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def get_user_preference(*args, **kwargs):
    """
    Wrapper for `get_user_preference` function in edx-platform.
    """
    backend_function = settings.FORUM_NOTIFIER_USER_API_BACKEND
    backend = import_module(backend_function)

    return backend.get_user_preference(*args, **kwargs)
