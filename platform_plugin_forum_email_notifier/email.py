"""Email module for platform_plugin_forum_email_notifier"""
from django.contrib.sites.models import Site
from edx_ace import ace
from edx_ace.message import MessageType
from openedx.core.lib.celery.task_utils import emulate_http_request


class ForumEmailNotification(MessageType):
    """
    Message type for forum email notification.
    """


forum_email_message_type = ForumEmailNotification()


def send_forum_email_notification(recipient, language, user_context):
    msg = forum_email_message_type.personalize(
        recipient=recipient,
        language=language,
        user_context=user_context,
    )
    with emulate_http_request(
        site=Site.objects.get_current(), user=user_context.get("user")
    ):
        ace.send(msg)
