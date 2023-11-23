""" Unit tests for commands in `platform_plugin_forum_email_notifier` plugin."""
from datetime import timedelta
from unittest import TestCase
from unittest.mock import Mock, call, patch

from django.core.management import CommandError

from platform_plugin_forum_email_notifier.management.commands.forum_digest import Command, DigestType, PreferenceOptions

COMMANDS_MODULE_PATH = "platform_plugin_forum_email_notifier.management.commands"


class ForumNotificationDigestMock(Mock):
    """
    Mock class for `ForumNotificationDigest` model.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __or__(self, other):
        return [self, other]


class TestCommand(TestCase):
    """
    Test suite for the Plugin Forum Email Notifier commands.
    """

    generate_digest_mock = patch(
        f"{COMMANDS_MODULE_PATH}.forum_digest.Command._generate_digest"
    )
    filter_mock = patch(
        f"{COMMANDS_MODULE_PATH}.forum_digest.ForumNotificationDigest.objects.filter"
    )
    send_digest_mock = patch(f"{COMMANDS_MODULE_PATH}.forum_digest.send_digest.delay")
    get_context_mock = patch(
        f"{COMMANDS_MODULE_PATH}.forum_digest.get_base_email_context"
    )

    def setUp(self) -> None:
        """
        Set up common test data for each test case.
        """
        self.command = Command()

    def test_handle_no_digest(self):
        """
        Check that the command raises an error when no digest is specified.
        """
        with self.assertRaises(CommandError) as context:
            self.command.handle(digest=None)

        self.assertEqual("You must specify a digest type", str(context.exception))

    @generate_digest_mock
    def test_handle_daily_digest(self, mock_generate_digest: Mock):
        """
        Check `_generate_digest` command behavior when a daily digest is specified.
        """
        self.command.handle(digest=DigestType.DAILY)

        mock_generate_digest.assert_called_once_with(
            PreferenceOptions.ALL_POSTS_DAILY_DIGEST,
            DigestType.DAILY,
            interval=timedelta(days=1),
        )

    @generate_digest_mock
    def test_handle_weekly_digest(self, mock_generate_digest: Mock):
        """
        Check `_generate_digest` command behavior when a weekly digest is specified.
        """
        self.command.handle(digest=DigestType.WEEKLY)

        mock_generate_digest.assert_called_once_with(
            PreferenceOptions.ALL_POSTS_WEEKLY_DIGEST,
            DigestType.WEEKLY,
            interval=timedelta(days=7),
        )

    @get_context_mock
    @filter_mock
    @send_digest_mock
    def test_generate_digest(
        self, mock_send_digest: Mock, mock_filter: Mock, mock_get_context: Mock
    ):
        """
        Check `_generate_digest` behavior when generating a digest.
        """
        context = {"foo": "bar"}
        mock_get_context.return_value = context
        mock_already_digest = ForumNotificationDigestMock(id=1)
        mock_never_digest = ForumNotificationDigestMock(id=2)
        mock_filter.return_value.exclude.side_effect = [
            mock_already_digest,
            mock_never_digest,
        ]

        self.command._generate_digest(  # pylint: disable=protected-access
            PreferenceOptions.ALL_POSTS_DAILY_DIGEST,
            DigestType.DAILY,
            timedelta(days=1),
        )

        self.assertEqual(2, mock_filter.call_count)
        mock_send_digest.assert_has_calls(
            [
                call(mock_already_digest.id, context=context),
                call(mock_never_digest.id, context=context),
            ]
        )
