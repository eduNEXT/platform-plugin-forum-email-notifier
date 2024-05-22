"""
Course Overviews module generalized definitions.
"""

from importlib import import_module

from django.conf import settings


def get_course_overview_or_none(*args, **kwargs):
    """
    Wrapper for `get_course_overview_or_none` function in edx-platform.
    """
    backend_function = settings.FORUM_NOTIFIER_COURSE_OVERVIEWS_BACKEND
    backend = import_module(backend_function)

    return backend.get_course_overview_or_none(*args, **kwargs)
