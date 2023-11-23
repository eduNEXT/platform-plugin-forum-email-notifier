""" Unit tests for celery tasks in `platform_plugin_forum_email_notifier` plugin."""
import json
from unittest import TestCase
from unittest.mock import Mock, patch

from ddt import data, ddt, unpack
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test.utils import override_settings
from edx_ace.recipient import Recipient

from platform_plugin_forum_email_notifier.models import (
    ForumNotificationDigest,
    ForumNotificationPreference,
    PreferenceOptions,
)
from platform_plugin_forum_email_notifier.tasks import (
    handle_digests,
    notify_users,
    send_digest,
    send_email_notification,
)
from platform_plugin_forum_email_notifier.utils import ForumObject

User = get_user_model()
TASKS_MODULE_PATH = "platform_plugin_forum_email_notifier.tasks"


@ddt
class TestSendEmailNotification(TestCase):
    """Unit test for `send_email_notification` task."""

    get_mock = patch(f"{TASKS_MODULE_PATH}.User.objects.get")
    get_course_overview_or_none_mock = patch(
        f"{TASKS_MODULE_PATH}.get_course_overview_or_none"
    )
    get_user_preference_mock = patch(f"{TASKS_MODULE_PATH}.get_user_preference")
    send_forum_email_notification_mock = patch(
        f"{TASKS_MODULE_PATH}.send_forum_email_notification"
    )

    def setUp(self) -> None:
        """
        Set up common test data for each test case.
        """
        self.send_email_notification_args = {
            "thread_id": "test-thread-id",
            "discussion": None,
            "course_id": "test-course-id",
            "body": "<p>test-body<p>",
            "title": "test-title",
            "url": "test-url/",
            "author_id": 1,
            "author_username": "test-author-username",
            "author_email": "test@author-email.com",
            "object_type": ForumObject.THREAD,
            "subscriber": 1,
            "context": {},
        }

    @get_mock
    @get_course_overview_or_none_mock
    @get_user_preference_mock
    @send_forum_email_notification_mock
    def test_send_email_notification_user_exists(
        self,
        mock_send_forum_email_notification: Mock,
        mock_get_user_preference: Mock,
        mock_get_course_overview_or_none: Mock,
        mock_get: Mock,
    ):
        """
        Check `send_email_notification` behavior when user exists.

        This test ensures that the function sends an email notification
        as expected when the user exists.

        Expected result:
            - Send an email notification to the user.
        """
        mock_user = Mock(spec=User, id=1, email="test@user-email.com")
        mock_get.return_value = mock_user
        mock_get_course_overview_or_none.return_value = Mock()
        mock_get_user_preference.return_value = "en"

        send_email_notification(**self.send_email_notification_args)

        mock_send_forum_email_notification.assert_called_once_with(
            recipient=Recipient(mock_user.id, mock_user.email),
            language="en",
            user_context={
                "user": mock_user,
                "course_id": "test-course-id",
                "course_name": mock_get_course_overview_or_none.return_value.display_name,
                "thread_id": "test-thread-id",
                "discussion": None,
                "body": "test-body",
                "title": "test-title",
                "url": "test-url/discussions/test-course-id/posts/test-thread-id",
                "author_id": 1,
                "author_username": "test-author-username",
                "author_email": "test@author-email.com",
                "object_type": ForumObject.THREAD,
            },
        )

    @get_mock
    def test_send_email_notification_user_does_not_exist(self, mock_get: Mock):
        """
        Check `send_email_notification` behavior when user does not exist.

        Expected result:
            - Raise `ObjectDoesNotExist` exception.
        """
        mock_get.side_effect = ObjectDoesNotExist

        with self.assertRaises(ObjectDoesNotExist):
            send_email_notification(**self.send_email_notification_args)

    @get_mock
    @get_course_overview_or_none_mock
    def test_send_email_notification_course_does_not_exist(
        self, mock_get_course_overview_or_none: Mock, mock_get: Mock
    ):
        """
        Check `send_email_notification` behavior when course does not exist.

        Expected result:
            - Raise `Exception` exception.
        """
        mock_get.return_value = Mock(spec=User, id=1, email="test@user-email.com")
        mock_get_course_overview_or_none.return_value = None

        with self.assertRaises(Exception):
            send_email_notification(**self.send_email_notification_args)

    @get_mock
    @get_course_overview_or_none_mock
    @get_user_preference_mock
    @send_forum_email_notification_mock
    @data(
        ("test-post-title", "test-discussion-id", "test-thread-id"),
        (None, "test-discussion-id", "test-discussion-id"),
    )
    @unpack
    def test_send_email_notification_post_title(
        self,
        post_title: str,
        discussion_id: str,
        expected_post_id: str,
        mock_send_forum_email_notification: Mock,
        mock_get_user_preference: Mock,
        mock_get_course_overview_or_none: Mock,
        mock_get: Mock,
    ):
        """
        Check `send_email_notification` behavior when post has title.

        Expected result:
            - The title of the post is used in the email notification.
            - The notification is sent to the user.
        """
        mock_user = Mock(spec=User, id=1, email="test@user-email.com")
        mock_get.return_value = mock_user
        mock_get_course_overview_or_none.return_value = Mock()
        mock_get_user_preference.return_value = "en"
        self.send_email_notification_args["title"] = post_title
        self.send_email_notification_args["discussion"] = {"id": discussion_id}

        send_email_notification(**self.send_email_notification_args)

        mock_send_forum_email_notification.assert_called_once_with(
            recipient=Recipient(mock_user.id, mock_user.email),
            language="en",
            user_context={
                "user": mock_user,
                "course_id": "test-course-id",
                "course_name": mock_get_course_overview_or_none.return_value.display_name,
                "thread_id": "test-thread-id",
                "discussion": self.send_email_notification_args["discussion"],
                "body": "test-body",
                "title": post_title,
                "url": f"test-url/discussions/test-course-id/posts/{expected_post_id}",
                "author_id": 1,
                "author_username": "test-author-username",
                "author_email": "test@author-email.com",
                "object_type": ForumObject.THREAD,
            },
        )


@ddt
class TestNotifyUsers(TestCase):
    """
    Unit test for `notify_users` task."""

    get_user_mock = patch(f"{TASKS_MODULE_PATH}.User.objects.get")
    get_forum_mock = patch(
        f"{TASKS_MODULE_PATH}.ForumNotificationPreference.objects.get"
    )
    get_staff_subscribers_mock = patch(f"{TASKS_MODULE_PATH}.get_staff_subscribers")
    get_subscribers_mock = patch(f"{TASKS_MODULE_PATH}.get_subscribers")
    send_email_notification_mock = patch(
        f"{TASKS_MODULE_PATH}.send_email_notification.delay"
    )
    handle_digests_mock = patch(f"{TASKS_MODULE_PATH}.handle_digests.delay")

    @get_user_mock
    @get_forum_mock
    @get_staff_subscribers_mock
    @get_subscribers_mock
    @send_email_notification_mock
    @handle_digests_mock
    def test_notify_users_thread(
        self,
        mock_handle_digests: Mock,
        mock_send_email_notification: Mock,
        mock_get_subscribers: Mock,
        mock_get_staff_subscribers: Mock,
        mock_get_forum_notification_preference: Mock,
        mock_get_user: Mock,
    ):
        """
        Check `notify_users` behavior for thread object type.

        Expected result:
            - Send an email notification to all subscribers.
            - A digest is created for all staff subscribers.
        """
        mock_get_subscribers.return_value = set([1])
        mock_get_staff_subscribers.return_value = set([2])
        mock_get_user.return_value = Mock(spec=User, id=1, email="test@user-email.com")
        mock_get_forum_notification_preference.return_value = Mock(
            spec=ForumNotificationPreference, preference=PreferenceOptions.ALL_POSTS
        )

        notify_users(
            thread_id="test-thread-id",
            discussion={},
            course_id="test-course-id",
            body="test-body",
            title="test-title",
            url="test-url/",
            author_id="test-author-id",
            author_username="test-author-username",
            author_email="test@author-email.com",
            object_type=ForumObject.THREAD,
            context={},
        )

        mock_send_email_notification.assert_called_with(
            "test-thread-id",
            {},
            "test-course-id",
            "test-body",
            "test-title",
            "test-url/",
            "test-author-id",
            "test-author-username",
            "test@author-email.com",
            ForumObject.THREAD,
            2,
            {},
        )
        mock_handle_digests.assert_called_with(
            "test-thread-id",
            {},
            "test-course-id",
            "test-body",
            "test-title",
            "test-url/",
            "test-author-id",
            "test-author-username",
            "test@author-email.com",
            ForumObject.THREAD,
        )

    def test_notify_users_invalid_object_type(self):
        """
        Check `notify_users` behavior for invalid object type.

        Expected result:
            - Raise `ValueError` exception.
        """
        with self.assertRaises(ValueError):
            notify_users(
                thread_id="test-thread_id",
                discussion={},
                course_id="test-course_id",
                body="test-body",
                title="test-title",
                url="test-url/",
                author_id="test-author_id",
                author_username="test-author_username",
                author_email="test-author_email",
                object_type="invalid-object-type",
                context={},
            )

    @get_user_mock
    @get_staff_subscribers_mock
    @get_subscribers_mock
    @send_email_notification_mock
    @handle_digests_mock
    def test_notify_users_user_does_not_exist(
        self,
        mock_handle_digests: Mock,
        mock_send_email_notification: Mock,
        mock_get_subscribers: Mock,
        mock_get_staff_subscribers: Mock,
        mock_get_user: Mock,
    ):
        """
        Check `notify_users` behavior when user does not exist.

        Expected result:
            - The `send_email_notification` task is not called.
            - A digest is created for all staff subscribers.
        """
        mock_get_subscribers.return_value = set()
        mock_get_staff_subscribers.return_value = set([1])
        mock_get_user.side_effect = User.DoesNotExist

        notify_users(
            thread_id="test-thread_id",
            discussion={},
            course_id="test-course_id",
            body="test-body",
            title="test-title",
            url="test-url/",
            author_id="test-author_id",
            author_username="test-author_username",
            author_email="test@author_email.com",
            object_type=ForumObject.THREAD,
            context={},
        )

        mock_send_email_notification.assert_not_called()
        mock_handle_digests.assert_called()

    @get_user_mock
    @get_forum_mock
    @get_staff_subscribers_mock
    @get_subscribers_mock
    @send_email_notification_mock
    @handle_digests_mock
    @data(
        PreferenceOptions.NONE,
        PreferenceOptions.ALL_POSTS_DAILY_DIGEST,
        PreferenceOptions.ALL_POSTS_WEEKLY_DIGEST,
    )
    def test_notify_users_user_preference_options(
        self,
        preference_option: PreferenceOptions,
        mock_handle_digests: Mock,
        mock_send_email_notification: Mock,
        mock_get_subscribers: Mock,
        mock_get_staff_subscribers: Mock,
        mock_get_forum_notification_preference: Mock,
        mock_get_user: Mock,
    ):
        """
        Check `notify_users` behavior for different user preference options.

        When preference_option is NONE, ALL_POSTS_DAILY_DIGEST or ALL_POSTS_WEEKLY_DIGEST,
        the user should not be notified.

        Expected result:
            - The `send_email_notification` task is not called.
            - A digest is created for all staff subscribers.
        """
        mock_get_subscribers.return_value = set([])
        mock_get_staff_subscribers.return_value = set([1])
        mock_get_user.return_value = Mock(spec=User, id=1, email="test@user-email.com")
        mock_get_forum_notification_preference.return_value = Mock(
            spec=ForumNotificationPreference,
            preference=preference_option,
        )

        notify_users(
            thread_id="test-thread_id",
            discussion={},
            course_id="test-course_id",
            body="test-body",
            title="test-title",
            url="test-url/",
            author_id="test-author_id",
            author_username="test-author_username",
            author_email="test@author_email.com",
            object_type=ForumObject.THREAD,
            context={},
        )

        mock_send_email_notification.assert_not_called()
        mock_handle_digests.assert_called()


class TestHandleDigests(TestCase):
    """Test case for `handle_digests` task."""

    def setUp(self):
        self.handle_digest_args = {
            "thread_id": "test-thread-id",
            "discussion": {},
            "course_id": "test-course-id",
            "body": "<p>test-body<p>",
            "title": "test-title",
            "url": "https://example.com/post",
            "author_id": "test-author-id",
            "author_username": "test-username",
            "author_email": "test@author-email.com",
            "object_type": ForumObject.THREAD,
        }

    @patch(f"{TASKS_MODULE_PATH}.ForumNotificationPreference.objects.filter")
    @patch(f"{TASKS_MODULE_PATH}.ForumNotificationDigest.objects.get_or_create")
    def test_handle_digests(
        self,
        mock_get_or_create: Mock,
        mock_filter: Mock,
    ):
        """
        Test `handle_digests` behavior when digest exists.

        Expected result:
            - A digest is created for each user with a digest preference.
        """
        user_mock = Mock()
        preference_mock = Mock()
        preference_mock.user = user_mock
        mock_filter.return_value.select_related.return_value = [preference_mock]
        digest_mock = Mock(threads_json="[]")
        mock_get_or_create.return_value = (digest_mock, True)

        handle_digests(**self.handle_digest_args)

        mock_filter.assert_called_once_with(
            preference__in=(
                PreferenceOptions.ALL_POSTS_DAILY_DIGEST,
                PreferenceOptions.ALL_POSTS_WEEKLY_DIGEST,
            ),
            course_id=self.handle_digest_args["course_id"],
        )
        mock_get_or_create.assert_called_once_with(
            user=user_mock,
            course_id=self.handle_digest_args["course_id"],
            defaults={
                "threads_json": "[]",
                "digest_type": preference_mock.preference,
            },
        )
        digest_mock.save.assert_called_once()


class TestSendDigest(TestCase):
    """Test cases for `send_digest` task."""

    @patch(f"{TASKS_MODULE_PATH}.send_digest_email_notification")
    @patch(f"{TASKS_MODULE_PATH}.ForumNotificationDigest.objects.get")
    def test_send_digest_no_digest(
        self, mock_get_digest: Mock, send_digest_email_mock: Mock
    ):
        """
        Check `send_digest` behavior when digest does not exist.

        Expected result:
            - Raise `ForumNotificationDigest.DoesNotExist` exception.
        """
        mock_get_digest.side_effect = ForumNotificationDigest.DoesNotExist

        with self.assertRaises(ForumNotificationDigest.DoesNotExist):
            send_digest("not-existing-digest", {})

        send_digest_email_mock.assert_not_called()

    @override_settings(LMS_ROOT_URL="https://example.com")
    @patch(f"{TASKS_MODULE_PATH}.ForumNotificationDigest.objects.get")
    @patch(f"{TASKS_MODULE_PATH}.get_course_overview_or_none")
    @patch(f"{TASKS_MODULE_PATH}.get_user_preference")
    @patch(f"{TASKS_MODULE_PATH}.send_digest_email_notification")
    def test_send_digest(
        self,
        mock_send_digest_email: Mock,
        mock_get_user_preference: Mock,
        mock_get_course: Mock,
        mock_get_digest: Mock,
    ):
        """
        Check `send_digest` behavior when digest exists.

        Expected result:
            - The digest is sent to the user.
            - The digest is updated.
        """
        digest_id = "test-digest-id"
        context = {}
        user_mock = Mock(id=1, email="test@user-email.com")
        digest_mock = Mock()
        digest_mock.user = user_mock
        digest_mock.threads_json = json.dumps([{"body": "<p>test-body<p>"}])
        mock_get_digest.return_value = digest_mock
        mock_get_course.return_value = Mock(display_name="test-course-name")
        mock_get_user_preference.return_value = "en"

        send_digest(digest_id, context)

        mock_get_digest.assert_called_once_with(id=digest_id)
        mock_get_course.assert_called_once_with(digest_mock.course_id)
        mock_get_user_preference.assert_called_once_with(user_mock, object)
        mock_send_digest_email.assert_called_once_with(
            recipient=Recipient(user_mock.id, user_mock.email),
            language="en",
            user_context={
                "user": user_mock,
                "course_id": digest_mock.course_id,
                "course_name": "test-course-name",
                "threads": [{"body": "test-body"}],
                "forum_notifier_url": (
                    f"https://example.com/courses/{digest_mock.course_id}/"
                    "instructor#view-forum_notifier"
                ),
                **context,
            },
        )
        self.assertIsNotNone(digest_mock.last_sent)
        self.assertEqual(digest_mock.threads_json, "[]")
