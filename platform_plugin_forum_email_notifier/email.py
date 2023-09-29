"""Email module to send ACE email messages to forum subscribers."""
from django.contrib.sites.models import Site
from edx_ace import ace
from edx_ace.message import MessageType

try:
    from openedx.core.lib.celery.task_utils import emulate_http_request
except ImportError:
    emulate_http_request = object


class ForumEmailNotification(MessageType):
    """
    Message type for forum email notification.
    """


class DigestEmailNotification(MessageType):
    """
    Message type for forum digest email notification.
    """


def send_forum_email_notification(recipient, language, user_context):
    """Send email notification for forum events to suscribers."""
    forum_email_message_type = ForumEmailNotification()
    msg = forum_email_message_type.personalize(
        recipient=recipient,
        language=language,
        user_context=user_context,
    )
    with emulate_http_request(
        site=Site.objects.get_current(), user=user_context.get("user")
    ):
        ace.send(msg)


def send_digest_email_notification(recipient, language, user_context):
    """Send email notification for forum events to suscribers."""
    forum_email_message_type = DigestEmailNotification()
    msg = forum_email_message_type.personalize(
        recipient=recipient,
        language=language,
        user_context=user_context,
    )
    with emulate_http_request(
        site=Site.objects.get_current(), user=user_context.get("user")
    ):
        ace.send(msg)
