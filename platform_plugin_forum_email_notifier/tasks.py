import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from edx_ace.recipient import Recipient
from edx_django_utils.monitoring import set_code_owner_attribute
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.user_api.preferences.api import get_user_preference

from platform_plugin_forum_email_notifier.email import send_forum_email_notification

log = logging.getLogger(__name__)
celery_log = logging.getLogger("edx.celery.task")

User = get_user_model()


@shared_task
@set_code_owner_attribute
def send_email_notification(
    subscriber, course_id, thread_body, thread_title, thread_url, thread_type
):
    """
    Serialize a course and writes it to ClickHouse.
    Arguments:
        subscriber: The id of the user to send the email notification
        course_id: The id of the course
        thread_body: The body of the new thread/comment/response
        thread_title: The title of the new thread/comment/response
        thread_url: The base URL of the thread
        thread_type: The type of the thread (thread, comment, response)
    """
    try:
        user = User.objects.get(id=subscriber)
    except User.DoesNotExist:
        log.warning(f"User {subscriber} does not exist")
        return

    course = CourseOverview.get_from_id(course_id)

    language_preference = get_user_preference(user, LANGUAGE_KEY)

    send_forum_email_notification(
        recipient=Recipient(user.id, user.email),
        language=language_preference,
        user_context={
            "user": user,
            "course_id": course_id,
            "course_name": course.display_name,
            "thread_body": thread_body,
            "thread_title": thread_title,
            "thread_url": thread_url,
            "thread_type": thread_type,
        },
    )
