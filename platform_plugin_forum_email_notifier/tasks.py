import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from edx_django_utils.monitoring import set_code_owner_attribute
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

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
        course_key_string: course key for the course to be exported
        connection_overrides (dict):  overrides to ClickHouse connection
            parameters specified in `settings.EVENT_SINK_CLICKHOUSE_BACKEND_CONFIG`.
    """
    celery_log.info(
        f"Sending email notification for course {subscriber} {course_id} {thread_body} {thread_title} {thread_url} {thread_type}"
    )
    try:
        user = User.objects.get(id=subscriber)
    except User.DoesNotExist:
        log.warning(f"User {subscriber} does not exist")
        return

    course = CourseOverview.get_from_id(course_id)

    plaintext = get_template("forum_email_notifier/forum_email_notification.txt")
    htmly = get_template("forum_email_notifier/forum_email_notification.html")

    d = {
        "user": user,
        "course_id": course_id,
        "thread_body": thread_body,
        "thread_title": thread_title,
        "thread_url": thread_url,
        "thread_type": thread_type,
    }

    subject = f"Activity in the discussion in {course.display_name}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email

    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
