""" Unit tests for utils in `platform_plugin_forum_email_notifier` plugin."""
from unittest import TestCase
from unittest.mock import Mock, patch

from ddt import data, ddt, unpack

from platform_plugin_forum_email_notifier.utils import get_staff_subscribers, get_subscribers

module_path = "platform_plugin_forum_email_notifier.utils"


@ddt
class TestUtils(TestCase):
    """Test suite for the Plugin Forum Email Notifier utils."""

    settings_mock = patch(f"{module_path}.settings")
    utils_mock = patch(f"{module_path}.comment_client_utils")
    forum_preference_mock = patch(
        f"{module_path}.ForumNotificationPreference.objects.filter"
    )

    @settings_mock
    @utils_mock
    @data(
        (
            {
                "collection": [{"subscriber_id": "1"}, {"subscriber_id": "2"}],
                "num_pages": 1,
                "page": 1,
            },
            {1, 2},
        ),
        (
            {
                "collection": [{"subscriber_id": "3"}, {"subscriber_id": "4"}],
                "num_pages": 1,
                "page": 1,
            },
            {3, 4},
        ),
    )
    @unpack
    def test_get_subscribers(
        self,
        request: dict,
        expected_result: set,
        mock_comment_client_utils: Mock,
        mock_settings: Mock,
    ):
        """
        Test that the function returns the correct set of subscribers.

        Expected result:
            - The function returns the correct set of subscribers
        """
        mock_comment_client_utils.perform_request.return_value = request
        mock_settings.PREFIX = "test-prefix"

        response = get_subscribers("thread-id")

        self.assertEqual(response, expected_result)

    @settings_mock
    @utils_mock
    def test_get_subscribers_no_subscribers(
        self, mock_comment_client_utils: Mock, mock_settings: Mock
    ):
        """
        Test that the function returns an empty set when there are no subscribers.

        Expected result:
            - The function returns an empty set
        """
        mock_comment_client_utils.perform_request.return_value = {
            "collection": [],
            "num_pages": 1,
            "page": 1,
        }
        mock_settings.PREFIX = "test-prefix"

        response = get_subscribers("thread-id")

        self.assertEqual(response, set())

    @forum_preference_mock
    def test_multiple_subscribers(self, mock_filter: Mock):
        """
        Test that the function returns the correct set of subscribers.

        Expected result:
            - The function returns the correct set of subscribers
        """
        first_mock, second_mock = Mock(), Mock()
        first_mock.user.id = 1
        second_mock.user.id = 2
        mock_filter.return_value = [first_mock, second_mock, first_mock]

        response = get_staff_subscribers("course_id")

        self.assertEqual(response, {1, 2})

    @forum_preference_mock
    def test_empty_response(self, mock_filter: Mock):
        """
        Test that the function returns an empty set when there are no subscribers.

        Expected result:
            - The function returns an empty set
        """
        mock_filter.return_value = []

        response = get_staff_subscribers("course_id")

        self.assertEqual(response, set())
