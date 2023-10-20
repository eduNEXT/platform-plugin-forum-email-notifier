"""
Open edX Filters needed for forum_notifier integration.
"""
import pkg_resources
from crum import get_current_request
from django.conf import settings
from django.template import Context, Template
from django.utils.translation import gettext as _
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment

from platform_plugin_forum_email_notifier.models import ForumNotificationPreference, PreferenceOptions

TEMPLATE_ABSOLUTE_PATH = "/instructor_dashboard/"
BLOCK_CATEGORY = "forum_notifier"


class AddInstructorNotifierTab(PipelineStep):
    """Add forum_notifier tab to instructor dashboard."""

    def run_filter(
        self, context, template_name
    ):  # pylint: disable=unused-argument, arguments-differ
        """Execute filter that modifies the instructor dashboard context.

        Args:
            context (dict): the context for the instructor dashboard.
            _ (str): instructor dashboard template name.
        """
        course = context["course"]
        template = Template(self.resource_string("static/html/forum_notifier.html"))

        request = get_current_request()
        if ForumNotificationPreference.objects.filter(
            user=request.user, course_id=course.id
        ).exists():
            current_preference = ForumNotificationPreference.objects.get(
                user=request.user, course_id=course.id
            ).preference
        else:
            current_preference = PreferenceOptions.NONE

        context.update(
            {
                "forum_notifier_url": getattr(settings, "FORUM_NOTIFIER_URL", ""),
                "options": PreferenceOptions.choices,
                "current_preference": current_preference,
            }
        )

        html = template.render(Context(context))
        frag = Fragment(html)

        frag.add_css(self.resource_string("static/css/forum_notifier.css"))
        frag.add_javascript(self.resource_string("static/js/forum_notifier.js"))

        section_data = {
            "fragment": frag,
            "section_key": BLOCK_CATEGORY,
            "section_display_name": _("Forum Notifications"),
            "course_id": str(course.id),
            "template_path_prefix": TEMPLATE_ABSOLUTE_PATH,
        }
        context["sections"].append(section_data)
        return {
            "context": context,
        }

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(
            "platform_plugin_forum_email_notifier", path
        )
        return data.decode("utf8")
