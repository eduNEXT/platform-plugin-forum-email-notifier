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
    Handle the FORUM_THREAD_CREATED event.
    """
    notify_users.delay(
        thread.id,
        thread.discussion,
        thread.course_id,
        thread.body,
        thread.title,
        thread.url,
        thread.user.id,
        thread.user.pii.username,
        thread.user.pii.email,
        object_type=ForumObject.THREAD,
    )


@receiver(FORUM_THREAD_RESPONSE_CREATED)
def forum_response_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handle the FORUM_THREAD_RESPONSE_CREATED event.
    """
    notify_users.delay(
        thread.id,
        thread.discussion,
        thread.course_id,
        thread.body,
        thread.title,
        thread.url,
        thread.user.id,
        thread.user.pii.username,
        thread.user.pii.email,
        object_type=ForumObject.RESPONSE,
    )


@receiver(FORUM_RESPONSE_COMMENT_CREATED)
def forum_comment_created_handler(
    signal, sender, thread, metadata, **kwargs
):  # pylint: disable=unused-argument
    """
    Handle the FORUM_RESPONSE_COMMENT_CREATED event.
    """
    notify_users.delay(
        thread.id,
        thread.discussion,
        thread.course_id,
        thread.body,
        thread.title,
        thread.url,
        thread.user.id,
        thread.user.pii.username,
        thread.user.pii.email,
        object_type=ForumObject.COMMENT,
    )
