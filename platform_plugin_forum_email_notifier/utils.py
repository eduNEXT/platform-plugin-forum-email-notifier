"""Utilities for the platform_plugin_forum_email_notifier plugin."""

from collections import namedtuple

try:
    from openedx.core.djangoapps.django_comment_common.comment_client import settings, utils
except ImportError:
    settings = object
    utils = object

Subscriber = namedtuple("Subscriber", ["id"])


def get_subscribers(thread_id):
    """Return a list of user ids subscribed to a thread."""
    page = 1
    num_pages = 100
    subscribers = []

    while page < num_pages:
        url = _url_for_thread_subscriptions(thread_id)
        params = {"page": page}
        response = utils.perform_request("get", url, params)

        for subscription in response["collection"]:
            subscribers.append(Subscriber(id=subscription["subscriber_id"]))

        num_pages = response["num_pages"]
        page = response["page"]
        page += 1

    return subscribers


def _url_for_thread_subscriptions(thread_id):
    """Return the url for the thread subscriptions endpoint in the forum service."""
    return f"{settings.PREFIX}/threads/{thread_id}/subscriptions"
