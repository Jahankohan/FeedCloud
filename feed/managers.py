from django.db import models


class FeedManager(models.Manager):
    def batch_get_feeds(self, priority: int, batch_size: int = 10):
        """
        Will yield batch of ACTIVE feeds

        used in periodic fetch_feed_entries
        """
        from feed.models import Feed

        queryset = (
            self.get_queryset()
            .filter(status=Feed.ACTIVE, priority=priority)
            .values_list("id", flat=True)
        )

        cursor = 0
        while True:
            batch = queryset[cursor : cursor + batch_size]
            if len(batch) == 0:
                break
            yield batch
            cursor = cursor + batch_size
