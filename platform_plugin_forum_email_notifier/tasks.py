"""Tasks for the platform_plugin_forum_email_notifier plugin."""
import json
import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from edx_ace.recipient import Recipient
from edx_django_utils.monitoring import set_code_owner_attribute

from platform_plugin_forum_email_notifier.edxapp_wrapper.course_overviews import get_course_overview_or_none
from platform_plugin_forum_email_notifier.edxapp_wrapper.lang_pref import LANGUAGE_KEY
from platform_plugin_forum_email_notifier.edxapp_wrapper.user_api import get_user_preference
from platform_plugin_forum_email_notifier.email import send_digest_email_notification, send_forum_email_notification
from platform_plugin_forum_email_notifier.models import (
    ForumNotificationDigest,
    ForumNotificationPreference,
    PreferenceOptions,
)
from platform_plugin_forum_email_notifier.utils import (
    ForumObject,
    get_simplified_text,
    get_staff_subscribers,
    get_subscribers,
)

log = logging.getLogger(__name__)
celery_log = logging.getLogger("edx.celery.task")

User = get_user_model()


@shared_task
@set_code_owner_attribute
def send_email_notification(
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
    subscriber,
    context,
):
    """
    Send a email notification to a subscriber user for forum updates.

    Arguments:
        thread_id (str): The thread id.
        discussion (dict): The discussion dict.
        course_id (str): The course id.
        body (str): The body of the post.
        title (str): The title of the post.
        url (str): The url of the post.
        author_id (str): The author id.
        author_username (str): The author username.
        author_email (str): The author email.
        object_type (str): The forum object type.
        subscriber (id): The subscriber id.
        context (dict): The context for the email.
    """
    try:
        user = User.objects.get(id=subscriber)
    except User.DoesNotExist:
        log.warning(f"User {subscriber} does not exist")
        return

    course = get_course_overview_or_none(course_id)

    language_preference = get_user_preference(user, LANGUAGE_KEY)
    post_id = thread_id if title else discussion.get("id")

    context.update(
        {
            "user": user,
            "course_id": course_id,
            "course_name": course.display_name,
            "thread_id": thread_id,
            "discussion": discussion,
            "body": get_simplified_text(body),
            "title": title,
            "url": f"{url}discussions/{course_id}/posts/{post_id}",
            "author_id": author_id,
            "author_username": author_username,
            "author_email": author_email,
            "object_type": object_type,
        }
    )

    send_forum_email_notification(
        recipient=Recipient(user.id, user.email),
        language=language_preference,
        user_context=context,
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
    context,
):
    """
    Get the subscribers for a thread and notify them.

    Arguments:
        thread_id (str): The thread id.
        discussion (dict): The discussion dict.
        course_id (str): The course id.
        body (str): The body of the post.
        title (str): The title of the post.
        url (str): The url of the post.
        author_id (str): The author id.
        author_username (str): The author username.
        author_email (str): The author email.
        object_type (str): The forum object type.
        context (dict): The context for the email.
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
        if subscriber in staff_subscribers:
            try:
                user = User.objects.get(id=subscriber)
                # Altough we are getting staff_subscribers whom have a preference of ALL_POSTS,
                # they can already be a subscriber of the thread, so we need to check if they
                # have a preference for the course
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
                continue
            except ForumNotificationPreference.DoesNotExist:
                pass
                # If the user does not have a preference and they already are a subscriber
                # we should notify them
        send_email_notification.delay(
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
            subscriber,
            context,
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

    Arguments:
        thread_id (str): The thread id.
        discussion (dict): The discussion dict.
        course_id (str): The course id.
        body (str): The body of the post.
        title (str): The title of the post.
        url (str): The url of the post.
        author_id (str): The author id.
        author_username (str): The author username.
        author_email (str): The author email.
        object_type (str): The forum object type.
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


@shared_task
@set_code_owner_attribute
def send_digest(
    digest_id,
    context,
):
    """
    Send the acumulated digest to the user.

    Arguments:
        digest_id (str): The digest id.
        context (dict): The context for the email.
    """
    digest = ForumNotificationDigest.objects.get(id=digest_id)
    user = digest.user

    threads = json.loads(digest.threads_json)

    for thread in threads:
        thread["body"] = get_simplified_text(thread.get("body"))

    course = get_course_overview_or_none(digest.course_id)
    lms_url = getattr(settings, "LMS_ROOT_URL", None)
    forum_notifier_url = (
        f"{lms_url}/courses/{digest.course_id}/instructor#view-forum_notifier"
    )

    language_preference = get_user_preference(user, LANGUAGE_KEY)

    context.update(
        {
            "user": user,
            "course_id": digest.course_id,
            "course_name": course.display_name,
            "threads": threads,
            "forum_notifier_url": forum_notifier_url,
        }
    )

    send_digest_email_notification(
        recipient=Recipient(user.id, user.email),
        language=language_preference,
        user_context=context,
    )

    digest.last_sent = timezone.now()
    digest.threads_json = "[]"
    digest.save()
