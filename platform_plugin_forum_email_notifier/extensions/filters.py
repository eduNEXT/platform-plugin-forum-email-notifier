"""
Open edX Filters needed for forum_notifier integration.
"""
import pkg_resources
from django.conf import settings
from django.template import Context, Template
from openedx_filters import PipelineStep
from web_fragments.fragment import Fragment

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
        html = template.render(Context(context))
        frag = Fragment(html)

        frag.add_css(self.resource_string("static/css/forum_notifier.css"))
        frag.add_javascript(self.resource_string("static/js/forum_notifier.js"))

        section_data = {
            "fragment": frag,
            "section_key": BLOCK_CATEGORY,
            "section_display_name": "Forum Notifications",
            "course_id": str(course.id),
            "template_path_prefix": TEMPLATE_ABSOLUTE_PATH,
        }
        context["sections"].append(section_data)
        return context

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string("platform_plugin_forum_email_notifier", path)
        return data.decode("utf8")
