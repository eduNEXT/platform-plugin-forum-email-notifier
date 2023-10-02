"""Signal handlers for forum events."""
from django.dispatch import receiver
from openedx_events.learning.signals import (
    FORUM_RESPONSE_COMMENT_CREATED,
    FORUM_THREAD_CREATED,
    FORUM_THREAD_RESPONSE_CREATED,
)

from platform_plugin_forum_email_notifier.tasks import notify_users
from platform_plugin_forum_email_notifier.utils import ForumObject


@receiver(FORUM_THREAD_CREATED)
def forum_thread_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handler for forum thread created event.
    """
    notify_users.delay(
        thread.id,
        thread.discussion,
        thread.course_id,
        thread.body,
        thread.title,
        thread.url,
        object_type=ForumObject.THREAD,
    )


@receiver(FORUM_THREAD_RESPONSE_CREATED)
def forum_response_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handler for forum response created event.
    """
    notify_users.delay(
        thread.id,
        thread.discussion,
        thread.course_id,
        thread.body,
        thread.title,
        thread.url,
        object_type=ForumObject.RESPONSE,
    )


@receiver(FORUM_RESPONSE_COMMENT_CREATED)
def forum_comment_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handler for forum comment created event.
    """
    notify_users.delay(
        thread.id,
        thread.discussion,
        thread.course_id,
        thread.body,
        thread.title,
        thread.url,
        object_type=ForumObject.COMMENT,
    )
