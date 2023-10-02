"""Tasks for the platform_plugin_forum_email_notifier plugin."""
import json
import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from edx_ace.recipient import Recipient
from edx_django_utils.monitoring import set_code_owner_attribute

try:
    from openedx.core.djangoapps.content.course_overviews.api import get_course_overview_or_none
    from openedx.core.djangoapps.lang_pref import LANGUAGE_KEY
    from openedx.core.djangoapps.user_api.preferences.api import get_user_preference
except ImportError:
    get_course_overview_or_none = object
    LANGUAGE_KEY = object
    get_user_preference = object


from platform_plugin_forum_email_notifier.email import send_forum_email_notification
from platform_plugin_forum_email_notifier.models import (
    ForumNotificationDigest,
    ForumNotificationPreference,
    PreferenceOptions,
)
from platform_plugin_forum_email_notifier.utils import ForumObject, get_staff_subscribers, get_subscribers

log = logging.getLogger(__name__)
celery_log = logging.getLogger("edx.celery.task")

User = get_user_model()


@shared_task
@set_code_owner_attribute
def send_email_notification(
    subscriber, course_id, thread_body, thread_title, thread_url, thread_type
):
    """
    Send a email notification to a subscriber user for forum updates.

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

    course = get_course_overview_or_none(course_id)

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


@shared_task
@set_code_owner_attribute
def notify_users(
    thread_id,
    discussion,
    course_id,
    body,
    title,
    url,
    author_id,
    author_username,
    author_email,
    object_type,
):
    """
    Get the subscribers for a thread and notify them.
    """
    if object_type == ForumObject.THREAD:
        subscribers = get_subscribers(thread_id)
    elif object_type in (ForumObject.RESPONSE, ForumObject.COMMENT):
        subscribers = get_subscribers(discussion.get("id"))
    else:
        raise ValueError(f"Invalid thread event type: {object_type}")

    staff_subscribers = get_staff_subscribers(course_id)

    subscribers = subscribers | staff_subscribers

    for subscriber in subscribers:
        try:
            user = User.objects.get(id=subscriber)
            preference = ForumNotificationPreference.objects.get(
                user=user, course_id=course_id
            )
            if preference.preference in (
                PreferenceOptions.NONE,
                PreferenceOptions.ALL_POSTS_DAILY_DIGEST,
                PreferenceOptions.ALL_POSTS_WEEKLY_DIGEST,
            ):
                continue
        except User.DoesNotExist:
            log.warning(f"User {subscriber} does not exist")
            return
        send_email_notification.delay(
            subscriber,
            str(course_id),
            body,
            title,
            url,
            author_id,
            author_username,
            author_email,
            object_type,
        )

    handle_digests.delay(
        thread_id,
        discussion,
        course_id,
        body,
        title,
        url,
        author_id,
        author_username,
        author_email,
        object_type,
    )


@shared_task
@set_code_owner_attribute
def handle_digests(
    thread_id,
    discussion,
    course_id,
    body,
    title,
    url,
    author_id,
    author_username,
    author_email,
    object_type,
):
    """
    Get the digest subscribers for a thread and notify them.
    """
    digest_preferences = ForumNotificationPreference.objects.filter(
        preference__in=(
            PreferenceOptions.ALL_POSTS_DAILY_DIGEST,
            PreferenceOptions.ALL_POSTS_WEEKLY_DIGEST,
        ),
        course_id=course_id,
    ).select_related("user")

    for preference in digest_preferences:
        digest, _ = ForumNotificationDigest.objects.get_or_create(
            user=preference.user,
            course_id=course_id,
            defaults={
                "threads_json": "[]",
                "digest_type": preference.preference,
            },
        )
        threads_json = json.loads(digest.threads_json)
        threads_json.append(
            {
                "thread_id": thread_id,
                "discussion": discussion,
                "body": body,
                "title": title,
                "url": url,
                "author_id": author_id,
                "author_username": author_username,
                "author_email": author_email,
                "object_type": object_type,
            }
        )

        digest.digest_type = preference.preference
        digest.threads_json = json.dumps(threads_json)
        digest.save()
