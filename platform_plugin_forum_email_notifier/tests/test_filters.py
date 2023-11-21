from unittest import TestCase
from unittest.mock import Mock, patch

from platform_plugin_forum_email_notifier.extensions.filters import (
    AddInstructorNotifierTab,
)
from platform_plugin_forum_email_notifier.models import PreferenceOptions

module_path = "platform_plugin_forum_email_notifier.extensions.filters"


class TestFilters(TestCase):
    """
    Test suite for the Plugin Forum Email Notifier filters.
    """

    def setUp(self) -> None:
        """
        Set up the test suite.
        """
        self.filter = AddInstructorNotifierTab(
            filter_type=Mock(), running_pipeline=Mock()
        )

    @patch(f"{module_path}.ForumNotificationPreference.objects.get")
    @patch(f"{module_path}.ForumNotificationPreference.objects.filter")
    @patch(f"{module_path}.get_current_request")
    def test_run_filter_forum_preferences_exists(
        self, mock_request: Mock, mock_filter: Mock, mock_get: Mock
    ):
        mock_request.return_value = Mock(user="test-user")
        mock_filter.return_value.exists.return_value = True
        mock_get.return_value.preference = PreferenceOptions.ALL_POSTS
        context = {"course": Mock(id="test-course-id"), "sections": []}
        template_name = "test-template-name"

        result = self.filter.run_filter(context, template_name)

        self.assertEqual(
            result["context"]["current_preference"], PreferenceOptions.ALL_POSTS
        )
        self.assertEqual(len(result["context"]["sections"]), 1)

    @patch(f"{module_path}.ForumNotificationPreference.objects.filter")
    @patch(f"{module_path}.get_current_request")
    def test_run_filter_forum_preferences_does_not_exists(
        self, mock_request: Mock, mock_filter: Mock
    ):
        mock_request.return_value = Mock(user="test-user")
        mock_filter.return_value.exists.return_value = False
        context = {"course": Mock(id="test-course-id"), "sections": []}
        template_name = "test-template-name"

        result = self.filter.run_filter(context, template_name)

        self.assertEqual(
            result["context"]["current_preference"], PreferenceOptions.NONE
        )
        self.assertEqual(len(result["context"]["sections"]), 1)
