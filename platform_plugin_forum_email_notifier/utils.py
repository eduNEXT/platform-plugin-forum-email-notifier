"""Utilities for the platform_plugin_forum_email_notifier plugin."""
from enum import IntEnum

from bs4 import BeautifulSoup
from django.contrib.sites.models import Site

try:
    from openedx.core.djangoapps.ace_common.template_context import get_base_template_context
    from openedx.core.djangoapps.django_comment_common.comment_client import settings, utils as comment_client_utils
except ImportError:
    settings = object
    comment_client_utils = object
    get_base_template_context = object

from platform_plugin_forum_email_notifier.models import ForumNotificationPreference, PreferenceOptions


def get_base_email_context() -> dict:
    """
    Return the base email context.

    Returns:
        dict: The base email context.
    """
    site = Site.objects.get_current()
    return get_base_template_context(site)


def truncate_text(text: str, max_length=160, suffix="..."):
    """
    Return a truncated version of the text.

    Args:
        text (str): The text to truncate.
        max_length (int, optional): The maximum length of the text. Defaults to 160.
        suffix (str, optional): The suffix to append to the truncated text. Defaults to "...".
    """
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}{suffix}"


def get_simplified_text(text: str) -> str:
    """
    Return the simplified text of a html string.

    If the text is longer than 160 characters, it will be truncated.

    Args:
        text (str): The html string.

    Returns:
        str: The simplified text.
    """
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text()
    return truncate_text(text)


def get_subscribers(thread_id):
    """Return a list of user ids subscribed to a thread."""
    page = 1
    num_pages = 100
    subscribers = set()

    while page < num_pages:
        url = _url_for_thread_subscriptions(thread_id)
        params = {"page": page}
        response = comment_client_utils.perform_request("get", url, params)

        for subscription in response["collection"]:
            subscribers.add(int(subscription["subscriber_id"]))

        num_pages = response["num_pages"]
        page = response["page"]
        page += 1

    return subscribers


def get_staff_subscribers(course_id):
    """Return a list of course staff users whom configured email preferences."""
    subscribers = set()

    preferences = ForumNotificationPreference.objects.filter(
        course_id=course_id, preference=PreferenceOptions.ALL_POSTS
    )

    for preference in preferences:
        subscribers.add(preference.user.id)

    return subscribers


def _url_for_thread_subscriptions(thread_id):
    """Return the url for the thread subscriptions endpoint in the forum service."""
    return f"{settings.PREFIX}/threads/{thread_id}/subscriptions"


class ForumObject(IntEnum):
    """Enum for forum objects that can trigger events."""

    THREAD = 1
    RESPONSE = 2
    COMMENT = 3
