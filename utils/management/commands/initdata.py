import os

from django.core.management.base import BaseCommand, CommandError

from authnz.models import User
from feed.models import Feed
from utils.exceptions import FeedCloudBaseException


class Command(BaseCommand):
    help = "Initialize some data for first use"

    def handle(self, *args, **options):
        admin_email = os.environ.get("ADMIN_EMAIL", None)
        if not admin_email:
            raise Exception(
                "Add ADMIN_EMAIL env variable, example: export ADMIN_EMAIL=123456"
            )
        admin_password = os.environ.get("ADMIN_PASSWORD", None)
        if not admin_password:
            raise Exception(
                "Add ADMIN_PASSWORD env variable, example: export ADMIN_PASSWORD=123456"
            )
        try:
            user = User.register_user(email=admin_email, password=admin_password)
        except FeedCloudBaseException as e:
            raise CommandError(e.detail)
        user.confirm_email()
        user.is_staff = True
        user.is_superuser = True
        user.save()
        # Initial feeds
        Feed.objects.bulk_create(
            [
                Feed(
                    link="http://www.nu.nl/rss/Algemeen",
                    status=Feed.ACTIVE,
                    creator=user,
                ),
                Feed(
                    link="https://feeds.feedburner.com/tweakers/mixed",
                    status=Feed.ACTIVE,
                    creator=user,
                ),
            ]
        )
        self.stdout.write(self.style.SUCCESS("Initializing of data was successful"))
