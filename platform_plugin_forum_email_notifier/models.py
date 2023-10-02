"""
Database models for forum_email_notifier.
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext as _
from model_utils.models import TimeStampedModel
from opaque_keys.edx.django.models import CourseKeyField

User = get_user_model()


class PreferenceOptions(models.IntegerChoices):
    """
    A model to store forum email notification preferences for a user.

    .. no_pii:
    """

    NONE = 1, _("None")
    ALL_POSTS = 2, _("All posts")
    ONLY_POSTS_IM_FOLLOWING = 3, _("Only posts I'm following")
    ALL_POSTS_DAILY_DIGEST = 4, _("All posts. (Daily digest)")
    ALL_POSTS_WEEKLY_DIGEST = 5, _("All posts. (Weekly digest)")


class ForumNotificationPreference(TimeStampedModel):
    """
    A model to store forum email notification preferences for a user.

    .. no_pii:
    """

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="forum_notification_preferences",
    )
    course_id = CourseKeyField(max_length=255, db_index=True)
    preference = models.IntegerField(
        choices=PreferenceOptions.choices, default=PreferenceOptions.NONE
    )

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        # TODO: return a string appropriate for the data fields
        return "<ForumNotificationPreference, ID: {}>".format(self.id)

    class Meta:
        ordering = ["-created"]
        unique_together = ["user", "course_id"]


class ForumNotificationDigest(TimeStampedModel):
    """
    A model to store forum email notification digests for a user.

    .. no_pii:
    """

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="forum_notification_digests",
    )
    course_id = CourseKeyField(max_length=255, db_index=True)
    threads_json = models.TextField()
    digest_type = models.IntegerField(choices=PreferenceOptions.choices)

    class Meta:
        ordering = ["-created"]
        unique_together = ["user", "course_id"]
