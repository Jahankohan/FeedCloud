import logging

from celery import group
from django.db.models import OuterRef, Subquery
from django.db.utils import DataError

from feed.models import Feed, Entry
from feedcloud.celery import app
from feedreader.exceptions import FeedReaderBaseException
from feedreader.feedreader import FeedReader


logger = logging.getLogger(__name__)


@app.task(name="schedule_fetch_feed_batch")
def schedule_fetch_feed_batch(priority: int):
    for feed_batch in Feed.objects.batch_get_feeds(priority=priority):
        group(fetch_feed_entries.s(feed_id) for feed_id in feed_batch).delay()


@app.task(name="fetch_feed_entries")
def fetch_feed_entries(feed_id: int):
    last_entry = (
        Entry.objects.filter(feed=OuterRef("pk"))
        .values("published_at")
        .order_by("-published_at")[:1]
    )
    try:
        feed = Feed.objects.annotate(last_modified=Subquery(last_entry)).get(id=feed_id)
    except Feed.DoesNotExist as e:
        logger.error(f"Feed {feed_id} does not exist.")
        return
    fr = FeedReader(feed.link, timeout=feed.timeout, last_modified=feed.last_modified)
    try:
        entries = fr.get_entries()
    except FeedReaderBaseException as e:
        logger.error(f"Feed {feed_id} got error {e}.")
        feed.feed_fail()
        return
    except Exception as e:
        logger.error(f"Feed {feed_id} got error {e}.")
        feed.feed_fail()
        raise
    try:
        Entry.objects.bulk_create(
            [
                Entry(
                    feed=feed,
                    title=entry.title[:200],
                    link=entry.url,
                    summary=entry.summary[:2000],
                    published_at=entry.published_at,
                )
                for entry in entries
            ],
            ignore_conflicts=True,
        )
    except DataError as e:
        logger.error(f"Feed {feed_id} got error {e}.")
        return

    if not feed.title:
        feed_info = fr.get_feed_info()
        feed.title = feed_info.title if feed_info else ""
        feed.save()
    feed.feed_success()
