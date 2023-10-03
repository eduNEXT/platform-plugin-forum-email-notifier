import logging
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from platform_plugin_forum_email_notifier.models import ForumNotificationDigest, PreferenceOptions
from platform_plugin_forum_email_notifier.tasks import send_digest

log = logging.getLogger(__name__)

from enum import Enum


class DigestType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class Command(BaseCommand):
    """
    Generates a digest of forum activity.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--digest",
            type=DigestType,
            help="the digest type to generate",
        )

    def handle(self, *args, **options):
        """
        Iterates through each course, serializes them into graphs, and saves
        those graphs to clickhouse.
        """
        digest = options["digest"]

        if not digest:
            raise CommandError("You must specify a digest type")

        if digest not in DigestType:
            raise CommandError("Invalid digest type. Must be one of: daily, weekly")

        if digest == DigestType.DAILY:
            self._generate_digest(
                PreferenceOptions.ALL_POSTS_DAILY_DIGEST,
                "daily",
                interval=timedelta(days=1),
            )
        elif digest == DigestType.WEEKLY:
            self._generate_digest(
                PreferenceOptions.ALL_POSTS_WEEKLY_DIGEST,
                "weekly",
                interval=timedelta(days=7),
            )

    def _generate_digest(self, filter, display_name, interval):
        log.info(f"Generating {display_name} digest")
        already_digested = ForumNotificationDigest.objects.filter(
            digest_type=filter, last_sent__lte=timezone.now() - interval
        ).exclude(threads_json="[]")
        never_digested = ForumNotificationDigest.objects.filter(
            digest_type=filter, last_sent__isnull=True
        ).exclude(threads_json="[]")

        digests = already_digested | never_digested

        for digest in digests:
            log.info(
                f"Generating {display_name} digest for user {digest.user.id} in course {digest.course_id}"
            )

            send_digest.delay(digest.id)
