from django.dispatch import receiver
from django.db.models.signals import post_save

from feed.tasks import fetch_feed_entries
from feed.models import Feed


@receiver(post_save, sender=Feed, dispatch_uid="update_feed")
def update_feed(sender, instance, **kwargs):
    """
    Run fetch_feed_entries background task

    it happen in 2 case

        1. after creation

        2. after updating link or force_update

    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    if instance.status == Feed.PENDING:
        fetch_feed_entries.apply_async((instance.id,))
