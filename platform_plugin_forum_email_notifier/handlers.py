"""Signal handlers for forum events."""
from enum import IntEnum

from django.dispatch import receiver
from openedx_events.learning.signals import (
    FORUM_RESPONSE_COMMENT_CREATED,
    FORUM_THREAD_CREATED,
    FORUM_THREAD_RESPONSE_CREATED,
)

from platform_plugin_forum_email_notifier.tasks import send_email_notification
from platform_plugin_forum_email_notifier.utils import get_subscribers


class ForumObject(IntEnum):
    THREAD = 1
    RESPONSE = 2
    COMMENT = 3


@receiver(FORUM_THREAD_CREATED)
def forum_thread_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handler for forum thread created event.
    """
    notify_users(thread, object_type=ForumObject.THREAD)


@receiver(FORUM_THREAD_RESPONSE_CREATED)
def forum_response_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handler for forum response created event.
    """
    notify_users(thread, object_type=ForumObject.RESPONSE)


@receiver(FORUM_RESPONSE_COMMENT_CREATED)
def forum_comment_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handler for forum comment created event.
    """
    notify_users(thread, object_type=ForumObject.COMMENT)


def notify_users(thread, object_type):
    """
    Get the subscribers for a thread and notify them.
    """
    if object_type == ForumObject.THREAD:
        subscribers = get_subscribers(thread.id)
    elif object_type in (ForumObject.RESPONSE, ForumObject.COMMENT):
        subscribers = get_subscribers(thread.discussion.get("id"))
    else:
        raise ValueError(f"Invalid thread event type: {object_type}")

    for subscriber in subscribers:
        send_email_notification.delay(
            subscriber.id,
            str(thread.course_id),
            thread.body,
            thread.title,
            thread.url,
            object_type,
        )
