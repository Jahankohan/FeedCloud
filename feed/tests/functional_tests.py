from datetime import datetime
from math import ceil
from typing import Iterable
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.urls import reverse

from authnz.models import User
from authnz.utils import generate_token
from feed.models import Feed, FollowFeed, Entry, EntryRead
from feed import tasks
from feedreader.entities import Entry as EntryEntity, Feed as FeedEntry
from feedreader.exceptions import FeedReaderBaseException


@pytest.fixture
def user_sample_data():
    return {
        "email": "test@test.com",
        "password": "Str0n5Pass",
    }


@pytest.fixture
def user_sample(user_sample_data):
    user = User.register_user(**user_sample_data)
    return user


@pytest.fixture
def user_sample_with_approved_email(user_sample):
    user_sample.confirm_email()
    return user_sample


@pytest.fixture
def admin_user_sample(user_sample):
    user_sample.is_staff = True
    user_sample.is_superuser = True
    user_sample.save()
    return user_sample


@pytest.fixture
def user_authorize_header(user_sample_with_approved_email):
    return {
        "HTTP_AUTHORIZATION": f"JWT {generate_token(user_sample_with_approved_email)}"
    }


@pytest.fixture
def feeds(user_sample):
    feeds_data = [
        {
            "title": "Feed title",
            "link": "https://www.feed.io",
            "creator": user_sample,
        },
        {
            "title": "Second feed",
            "link": "https://www.second-feed.io",
            "creator": user_sample,
        },
        {
            "title": "Last feed",
            "link": "https://www.last-feed.io",
            "creator": user_sample,
        },
    ]
    Feed.objects.bulk_create([Feed(**feed) for feed in feeds_data])


@pytest.fixture
def entries(feeds):
    entries_data = [
        {
            "title": "entry title first",
            "summary": "entry summary",
            "link": "my-link1.io",
            "published_at": datetime.now().astimezone(),
            "feed_id": 1,
        },
        {
            "title": "entry title first",
            "summary": "entry summary",
            "link": "my-link2.io",
            "published_at": datetime.now().astimezone(),
            "feed_id": 1,
        },
    ]
    Entry.objects.bulk_create([Entry(**entry) for entry in entries_data])


def feed_reader_entries():
    return [
        EntryEntity(
            title="entry title first",
            summary="entry summary",
            url=f"my-link{uuid4()}.io",
            published_at=datetime.now().astimezone(),
        ),
        EntryEntity(
            title="entry title second",
            summary="entry summary",
            url=f"my-link{uuid4()}.io",
            published_at=datetime.now().astimezone(),
        ),
    ]


def feed_reader_feed():
    return FeedEntry("My feed", "Some url")


class TestFeed:
    @pytest.mark.django_db
    def test_add_feed_by_admin_correctly(
        self, client, user_authorize_header, admin_user_sample
    ):
        data = {"title": "Feed title", "link": "https://www.feed.io"}
        url = reverse("feeds")
        resp = client.post(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 201
        resp_json = resp.json()
        assert isinstance(resp_json["data"], dict)
        assert resp_json["data"]["title"] == data["title"]
        assert resp_json["data"]["link"] == data["link"]
        assert resp_json["data"]["creator"]["email"] == admin_user_sample.email
        assert resp_json["data"].get("status", False)
        assert resp_json["data"].get("priority", False)
        assert resp_json["data"].get("created_at", False)
        assert Feed.objects.count() == 1

    @pytest.mark.django_db
    def test_add_feed_by_user_correctly(self, client, user_authorize_header):
        data = {"title": "Feed title", "link": "https://www.feed.io"}
        url = reverse("feeds")
        resp = client.post(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 201
        resp_json = resp.json()
        assert isinstance(resp_json["data"], dict)
        assert resp_json["data"]["title"] == data["title"]
        assert resp_json["data"]["link"] == data["link"]
        assert resp_json["data"].get("creator", False)
        assert resp_json["data"].get("status", False)
        assert resp_json["data"].get("priority", False)
        assert resp_json["data"].get("created_at", False)
        assert Feed.objects.count() == 1

    @pytest.mark.django_db
    def test_add_duplicate_feed_fail(self, client, user_authorize_header):
        data = {"title": "Feed title", "link": "https://www.feed.io"}
        url = reverse("feeds")
        resp = client.post(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 201
        resp = client.post(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 409
        assert Feed.objects.count() == 1

    @pytest.mark.django_db
    def test_add_feed_invalid_link_fail(self, client, user_authorize_header):
        data = {"title": "Feed title", "link": "my-link"}
        url = reverse("feeds")
        resp = client.post(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 400
        assert Feed.objects.count() == 0

    @pytest.mark.django_db
    def test_list_feed_functionality(self, client, feeds, user_authorize_header):
        url = reverse("feeds")

        # Pending feeds
        resp = client.get(url, content_type="application/json", **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 0

        # Active feeds
        Feed.objects.all().update(status=Feed.ACTIVE)
        resp = client.get(url, content_type="application/json", **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 3

        # pagination
        pagination = "?index=1&size=1"
        resp = client.get(
            f"{url}{pagination}",
            content_type="application/json",
            **user_authorize_header,
        )
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 1
        assert resp_json["total"] == 3

        # search
        query_param = "?title=last"
        resp = client.get(
            f"{url}{query_param}",
            content_type="application/json",
            **user_authorize_header,
        )
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 1
        assert "last" in resp_json["data"][0]["title"].lower()

    @pytest.mark.django_db
    def test_feed_priority(self, feeds):
        feed = Feed.objects.first()
        assert feed.priority == Feed.HIGH
        feed.feed_fail()
        assert feed.priority == Feed.LOW
        feed.feed_success()
        assert feed.priority == Feed.HIGH
        feed.feed_success()
        assert feed.priority == Feed.HIGH
        feed.feed_success()
        assert feed.priority == Feed.HIGH
        feed.feed_fail()
        assert feed.priority == Feed.LOW
        feed.feed_fail()
        assert feed.priority == Feed.STOP
        assert feed.status == Feed.ERROR
        feed.feed_fail()
        assert feed.priority == Feed.STOP
        assert feed.status == Feed.ERROR

    @pytest.mark.django_db
    def test_admin_list_feed_functionality(
        self, client, feeds, user_authorize_header, admin_user_sample
    ):
        url = reverse("feeds")
        # filter Active feeds
        query_param = "?status=A"
        resp = client.get(
            f"{url}{query_param}",
            content_type="application/json",
            **user_authorize_header,
        )
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 0

        # filter Pending feeds
        query_param = "?status=P"
        resp = client.get(
            f"{url}{query_param}",
            content_type="application/json",
            **user_authorize_header,
        )
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 3

        # admin fields
        for feed_data in resp_json["data"]:
            assert feed_data.get("creator", False)
            assert feed_data.get("status", False)
            assert feed_data.get("priority", False)
            assert feed_data.get("created_at", False)

    @pytest.mark.django_db
    def test_follow_feed_functionality(self, client, feeds, user_authorize_header):
        url = reverse("feed_follow")
        resp = client.get(url, content_type="application/json", **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()
        assert resp_json["total"] == 0

        # follow
        data = {"id": 1}
        resp = client.post(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 200
        assert FollowFeed.objects.count() == 1
        resp = client.get(url, content_type="application/json", **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()
        assert resp_json["total"] == 1
        assert resp_json["data"][0]["id"] == data["id"]

        # unfollow
        url = reverse("feed_unfollow", args=(data["id"],))
        resp = client.delete(
            url, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 204
        assert FollowFeed.objects.count() == 0

    @pytest.mark.django_db
    def test_list_feed_created_by_user(self, client, feeds, user_authorize_header):
        url = reverse("my_feeds")

        resp = client.get(url, content_type="application/json", **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 3
        # return pending feeds
        assert Feed.objects.filter(status=Feed.PENDING).count() == 3

        # my_feeds fields
        for feed_data in resp_json["data"]:
            assert feed_data.get("creator", False)
            assert feed_data.get("status", False)
            assert feed_data.get("priority", False)
            assert feed_data.get("created_at", False)

    @pytest.mark.django_db
    def test_batch_get_feeds(self, user_sample):
        data = {"title": "Title 1", "link": "feed.io"}
        feed_number = 27
        feed_batch_size = 5
        feeds = [
            Feed(
                title=f"{data['title']}{i}",
                link=f"{data['link']}{i}",
                creator=user_sample,
            )
            for i in range(feed_number)
        ]
        Feed.objects.bulk_create(feeds)
        # PENDING feeds
        assert (
            len(
                list(
                    Feed.objects.batch_get_feeds(priority=2, batch_size=feed_batch_size)
                )
            )
            == 0
        )

        Feed.objects.all().update(status=Feed.ACTIVE)
        batch_count = 0
        for batch_feed in Feed.objects.batch_get_feeds(
            priority=2, batch_size=feed_batch_size
        ):
            assert len(batch_feed) <= feed_batch_size
            assert isinstance(batch_feed, Iterable)
            for feed in batch_feed:
                assert isinstance(feed, int)
            batch_count += 1
        assert batch_count == ceil(feed_number / feed_batch_size)


class TestEntry:
    @pytest.mark.django_db
    def test_entries_list_functionality(self, client, user_authorize_header, entries):
        # entries of feed
        url = reverse("feed_entries", args=(1,))
        resp = client.get(url, content_type="application/json", **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 2
        for entry in resp_json["data"]:
            assert entry.get("id", False)
            assert entry.get("title", False)
            assert entry.get("link", False)
            assert entry.get("summary", False)
            assert entry.get("published_at", False)
            assert entry.get("feed", False)
            assert entry["feed"].get("id", False)
            assert entry["feed"].get("title", False)

        # all entries
        url = reverse("entries")
        resp = client.get(url, content_type="application/json", **user_authorize_header)
        assert resp.status_code == 200
        resp_json = resp.json()

        assert isinstance(resp_json["data"], list)
        assert resp_json["index"] == 0
        assert resp_json["total"] == 2
        for entry in resp_json["data"]:
            assert entry.get("id", False)
            assert entry.get("title", False)
            assert entry.get("link", False)
            assert entry.get("summary", False)
            assert entry.get("published_at", False)
            assert entry.get("feed", False)
            assert entry["feed"].get("id", False)
            assert entry["feed"].get("title", False)

    @pytest.mark.django_db
    def test_entries_read_functionality(self, client, user_authorize_header, entries):
        assert Entry.objects.count() == 2
        assert EntryRead.objects.count() == 0
        url = reverse("entry_read")
        data = {"id": 1}
        resp = client.post(
            url, data, content_type="application/json", **user_authorize_header
        )
        assert resp.status_code == 200

        assert EntryRead.objects.count() == 1

        # filter read
        url = reverse("entries")
        query_param = "?read=true"
        resp = client.get(
            f"{url}{query_param}",
            content_type="application/json",
            **user_authorize_header,
        )
        assert resp.status_code == 200
        resp_json = resp.json()
        assert resp_json["total"] == 1
        assert resp_json["data"][0]["id"] == data["id"]

        # filter unread
        url = reverse("entries")
        query_param = "?read=false"
        resp = client.get(
            f"{url}{query_param}",
            content_type="application/json",
            **user_authorize_header,
        )
        assert resp.status_code == 200
        resp_json = resp.json()
        assert resp_json["total"] == 1
        assert resp_json["data"][0]["id"] != data["id"]


class MockFeedReader:
    def __init__(self, *args, **kwargs):
        pass

    def get_feed_info(self):
        return feed_reader_feed()

    def get_entries(self):
        return feed_reader_entries()


class TestTasks:
    @pytest.mark.django_db
    @patch("feed.tasks.FeedReader", MockFeedReader)
    def test_fetch_feed_entries_successfully(self, feeds):
        feed_id = 1
        tasks.fetch_feed_entries(feed_id)
        entries = Entry.objects.all()
        assert len(entries) == 2
        for entry in entries:
            assert entry.feed_id == feed_id

        feed = Feed.objects.get(id=feed_id)
        assert feed.priority == Feed.HIGH
        assert feed.status == Feed.ACTIVE

    @pytest.mark.django_db
    @patch("feed.tasks.FeedReader.get_entries", side_effect=Exception)
    def test_fetch_feed_entries_with_exception(self, mock_get_entries, feeds):
        feed_id = 1
        with pytest.raises(Exception):
            tasks.fetch_feed_entries(feed_id)

        assert Entry.objects.exists() is False

        feed = Feed.objects.get(id=feed_id)
        assert feed.priority == Feed.LOW
        assert feed.status == Feed.ERROR

    @pytest.mark.django_db
    @patch("feed.tasks.FeedReader.get_entries", side_effect=FeedReaderBaseException)
    def test_fetch_feed_entries_with_feed_reader_base_exception(
        self, mock_get_entries, feeds
    ):
        feed_id = 1
        tasks.fetch_feed_entries(feed_id)

        assert Entry.objects.exists() is False

        feed = Feed.objects.get(id=feed_id)
        assert feed.priority == Feed.LOW
        assert feed.status == Feed.ERROR

    @pytest.mark.django_db
    @patch("feed.tasks.FeedReader", MockFeedReader)
    def test_fetch_feed_entries_feed_with_no_title(self, feeds):
        feed_id = 1
        feed = Feed.objects.get(id=feed_id)
        feed.title = ""
        feed.save()
        tasks.fetch_feed_entries(feed_id)

        feed = Feed.objects.get(id=feed_id)
        assert feed.title == feed_reader_feed().title

    @pytest.mark.django_db
    @patch("feed.tasks.FeedReader", MockFeedReader)
    def test_schedule_fetch_feed_batch_successfully(self, feeds):
        Feed.objects.update(status=Feed.ACTIVE)
        tasks.schedule_fetch_feed_batch(Feed.HIGH)
        assert Entry.objects.count() == Feed.objects.count() * len(
            feed_reader_entries()
        )
