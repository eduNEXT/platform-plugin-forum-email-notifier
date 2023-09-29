from django.dispatch import receiver
from openedx_events.learning.signals import FORUM_COMMENT_CREATED, FORUM_RESPONSE_CREATED, FORUM_THREAD_CREATED

from platform_plugin_forum_email_notifier.tasks import send_email_notification
from platform_plugin_forum_email_notifier.utils import get_subscribers


@receiver(FORUM_THREAD_CREATED)
def forum_thread_created_handler(signal, sender, thread, metadata, **kwargs):
    """
    Handler for forum thread created event.
    """
    notify_users(thread, type="thread")


@receiver(FORUM_RESPONSE_CREATED)
def forum_response_created_handler(signal, sender, thread, metadata, **kwargs):
    """
    Handler for forum response created event.
    """
    notify_users(thread, type="response")


@receiver(FORUM_COMMENT_CREATED)
def forum_comment_created_handler(signal, sender, thread, metadata, **kwargs):
    """
    Handler for forum comment created event.
    """
    notify_users(thread, type="comment")


def notify_users(thread, type):
    """
    Get the subscribers for a thread and notify them.
    """
    if type == "thread":
        subscribers = get_subscribers(thread.id)
    elif type == "response" or type == "comment":
        subscribers = get_subscribers(thread.discussion.get("id"))
    else:
        raise ValueError(f"Invalid thread event type: {type}")

    for subscriber in subscribers:
        send_email_notification.delay(
            subscriber.id,
            str(thread.course_id),
            thread.body,
            thread.title,
            thread.url,
            type,
        )
