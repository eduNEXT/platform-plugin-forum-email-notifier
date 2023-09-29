"""Utilities for the platform_plugin_forum_email_notifier plugin."""

from collections import namedtuple

Subscriber = namedtuple("Subscriber", ["id"])


def get_subscribers(thread_id):
    """"""
    subscribers = [Subscriber(subscriber_id) for subscriber_id in range(0, 5)]
    return subscribers
