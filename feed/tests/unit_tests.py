from unittest.mock import patch

import pytest

from feed.models import Feed
from feed import tasks
from feedreader.exceptions import FeedReaderBaseException


class TestTasks:
    @patch("feed.tasks.Feed")
    def test_fetch_feed_entries_feed_does_not_exist(self, mock_feed):
        feed_id = 1
        mock_feed.DoesNotExist = Feed.DoesNotExist
        mock_feed.objects.annotate().get.side_effect = Feed.DoesNotExist
        tasks.fetch_feed_entries(feed_id)
        assert (
            mock_feed.objects.annotate().get.assert_called_once_with(id=feed_id) is None
        )

    @patch("feed.tasks.FeedReader.get_entries", side_effect=FeedReaderBaseException)
    @patch("feed.tasks.Feed")
    def test_fetch_feed_entries_feed_reader_base_exception(
        self, mock_feed, mock_get_entries
    ):
        feed_id = 1
        tasks.fetch_feed_entries(feed_id)
        assert (
            mock_feed.objects.annotate().get.assert_called_once_with(id=feed_id) is None
        )
        assert mock_get_entries.assert_called_once_with() is None
        assert (
            mock_feed.objects.annotate().get().feed_fail.assert_called_once_with()
            is None
        )

    @patch("feed.tasks.FeedReader.get_entries", side_effect=Exception)
    @patch("feed.tasks.Feed")
    def test_fetch_feed_entries_feed_reader_exception(
        self, mock_feed, mock_get_entries
    ):
        feed_id = 1
        with pytest.raises(Exception):
            tasks.fetch_feed_entries(feed_id)
        assert (
            mock_feed.objects.annotate().get.assert_called_once_with(id=feed_id) is None
        )
        assert mock_get_entries.assert_called_once_with() is None
        assert (
            mock_feed.objects.annotate().get().feed_fail.assert_called_once_with()
            is None
        )

    @patch("feed.tasks.FeedReader.get_entries")
    @patch("feed.tasks.Feed")
    def test_fetch_feed_entries_successful(self, mock_feed, mock_get_entries):
        feed_id = 1
        tasks.fetch_feed_entries(feed_id)
        assert (
            mock_feed.objects.annotate().get.assert_called_once_with(id=feed_id) is None
        )
        assert mock_get_entries.assert_called_once_with() is None
        assert (
            mock_feed.objects.annotate().get().feed_success.assert_called_once_with()
            is None
        )
        assert mock_feed.objects.annotate().get().feed_fail.assert_not_called() is None
