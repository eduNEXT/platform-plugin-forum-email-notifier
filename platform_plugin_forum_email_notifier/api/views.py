from rest_framework.response import Response
from rest_framework.views import APIView

from platform_plugin_forum_email_notifier.models import ForumNotificationPreference, PreferenceOptions


class ForumEmailNotificationPreferenceAPIView(APIView):
    """
    API endpoint that allows to update the forum email notification preference.
    """

    def get(self, request, course_id, format=None):
        """
        Get the forum email notification preference for the user.
        """
        try:
            preference = ForumNotificationPreference.objects.get(
                user=request.user,
                course_id=course_id,
            )
            return Response({"preference": preference.preference})
        except ForumNotificationPreference.DoesNotExist:
            return Response({"preference": PreferenceOptions.NONE})

    def put(self, request, course_id, format=None):
        """
        Update the forum email notification preference for the user.
        """
        preference = request.data.get("preference")

        preference_obj, _ = ForumNotificationPreference.objects.get_or_create(
            user=request.user,
            course_id=course_id,
            defaults={"preference": PreferenceOptions.NONE},
        )

        preference_obj.preference = preference
        preference_obj.save()
        return Response({"preference": preference})
