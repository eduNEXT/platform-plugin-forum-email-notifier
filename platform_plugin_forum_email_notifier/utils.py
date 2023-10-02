"""Utilities for the platform_plugin_forum_email_notifier plugin."""
from collections import namedtuple
from enum import IntEnum

try:
    from openedx.core.djangoapps.django_comment_common.comment_client import settings, utils
except ImportError:
    settings = object
    utils = object

from platform_plugin_forum_email_notifier.models import ForumNotificationPreference, PreferenceOptions


def get_subscribers(thread_id):
    """Return a list of user ids subscribed to a thread."""
    page = 1
    num_pages = 100
    subscribers = set()

    while page < num_pages:
        url = _url_for_thread_subscriptions(thread_id)
        params = {"page": page}
        response = utils.perform_request("get", url, params)

        for subscription in response["collection"]:
            subscribers.add(int(subscription["subscriber_id"]))

        num_pages = response["num_pages"]
        page = response["page"]
        page += 1

    return subscribers


def get_staff_subscribers(course_id):
    """Return a list of user ids subscribed to a thread."""
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
    THREAD = 1
    RESPONSE = 2
    COMMENT = 3
