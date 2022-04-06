from django.conf import settings
from django.db import models
from django.utils.translation import gettext

from feed.managers import FeedManager


class Feed(models.Model):
    ACTIVE = "A"
    PENDING = "P"
    ERROR = "E"
    status_choices = (
        (ACTIVE, "ACTIVE"),
        (PENDING, "PENDING"),
        (ERROR, "ERROR"),
    )
    HIGH = 2
    LOW = 1
    STOP = 0
    priority_choices = (
        (HIGH, "HIGH"),
        (LOW, "LOW"),
        (STOP, "STOP"),
    )
    timeout_choices = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(
        max_length=100, help_text=gettext("Title of feed."), default=None, null=True
    )
    link = models.URLField(
        max_length=200, unique=True, db_index=True, help_text=gettext("Link of feed.")
    )
    status = models.CharField(
        max_length=1,
        choices=status_choices,
        default=PENDING,
        db_index=True,
        help_text=gettext("Status of feed."),
    )
    priority = models.SmallIntegerField(
        default=2,
        choices=priority_choices,
        db_index=True,
        help_text=gettext("Priority of feed."),
    )
    timeout = models.SmallIntegerField(
        default=2,
        choices=timeout_choices,
        help_text=gettext("Timeout of fetching of feed."),
    )
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="FollowFeed", related_name="feed_followed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ("title",)

    objects = FeedManager()

    def __str__(self):
        return "Feed: {}".format(self.title)

    def feed_success(self):
        """
        it happen when fetching feed succeed

        :return:
        """
        increase_done = self._increase_priority()
        status_change_done = self._check_feed_status_success()
        if increase_done or status_change_done:
            self.save()

    def feed_fail(self):
        """
        it happen when fetching feed face an error
        :return:
        """
        decrease_done = self._decrease_priority()
        status_change_done = self._check_feed_status_fail()
        if decrease_done or status_change_done:
            self.save()

    def _increase_priority(self):
        """
        Increase priority every time we have success in fetching feeds

        :return: True if increased else if not increased
        """
        if self.priority < self.HIGH:
            self.priority += 1
            return True

    def _check_feed_status_success(self):
        """
        in 2 case status could be PENDING in this method

            1. at creation and with priority HIGH (2)

            2. after update by creator or admin (update link or force_update)

        so we check status and change it to ACTIVE to participate in periodic task
        :return: True if status changed else if not increased
        """
        if self.status == self.PENDING:
            self.status = self.ACTIVE
            return True

    def _decrease_priority(self):
        """
        Decrease feed priority

        if priority rich STOP (zero) status will update to ERROR

        :return: True if status decreased else if not decreased
        """
        if self.priority > self.STOP:
            self.priority -= 1
            if self.priority == self.STOP:
                self.status = self.ERROR
            return True

    def _check_feed_status_fail(self):
        """
        Decrease feed priority

        it happen when fetching feed face an error

        if priority rich STOP (zero) status will update to ERROR
        :return:
        """
        if self.status == self.PENDING:
            self.status = self.ERROR
            return True


class FollowFeed(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "feed")


class Entry(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text=gettext("Title of entry."))
    link = models.CharField(
        max_length=500, unique=True, help_text=gettext("Link of entry.")
    )
    summary = models.CharField(max_length=2000, help_text=gettext("Summary of entry."))
    created_at = models.DateTimeField(
        auto_now_add=True, help_text=gettext("Creation time of entry.")
    )
    published_at = models.DateTimeField(help_text=gettext("Publish Time of entry."))
    reads = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="EntryRead", related_name="entries_read"
    )

    class Meta:
        verbose_name_plural = "entries"
        ordering = ("-published_at",)

    def __str__(self):
        return "Feed entry: {}".format(self.title)


class EntryRead(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "entry")
