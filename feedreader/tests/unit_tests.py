import json
from typing import Optional

import pytest
from dateutil.parser import parse

from feedreader.feedreader import FeedReader
from feedreader.entities import Entry
from feedreader.exceptions import FeedReaderBaseException, UnSuccessfulRequestException


class MockResponse:
    def __init__(self, content, status_code):
        self.content = content
        self.status_code = status_code


class MockRequestAgent:
    def __init__(self, content: Optional[dict] = None, status_code: int = 200):
        self.content = content
        self.status_code = status_code

    def get(self, url, timeout, headers):
        return MockResponse(self.content, self.status_code)


class MockParsedFeed:
    def __init__(self, bozo, bozo_exception, entries):
        self.bozo = bozo
        self.bozo_exception = bozo_exception
        self.entries = entries


class MockParserAgent:
    def __init__(
        self,
        bozo: bool = False,
        bozo_exception: Exception = None,
        content: Optional[dict] = None,
    ):
        self.bozo = bozo
        self.bozo_exception = bozo_exception
        self.feed = content["feed"] if content and content.get("feed") else {}
        self.entries = content["entries"] if content and content.get("entries") else []

    def parse(self, content):
        return MockParserAgent(self.bozo, self.bozo_exception, content=content)


@pytest.fixture
def sample_content():
    with open("feedreader/tests/sample_content.json") as file:
        content = file.read()
    return json.loads(content)


class TestFeedParser:
    def test_un_successful_response_status_code(self):
        fp = FeedReader(
            "sample_url",
            request_agent=MockRequestAgent(status_code=201),
            parser_agent=MockParserAgent(),
        )
        with pytest.raises(UnSuccessfulRequestException):
            fp.get_entries()

    def test_exception_occurring_feed_parser(self):
        fp = FeedReader(
            "sample_url",
            request_agent=MockRequestAgent(),
            parser_agent=MockParserAgent(True, Exception()),
        )
        with pytest.raises(FeedReaderBaseException):
            fp.get_entries()

    def test_get_feed_info_success(self, sample_content):
        sample_url = "sample_url"
        fp = FeedReader(
            sample_url,
            request_agent=MockRequestAgent(content=sample_content),
            parser_agent=MockParserAgent(),
        )
        feed = fp.get_feed_info()
        assert feed.title == sample_content["feed"]["title"]
        assert feed.url == sample_url

    def test_get_entries_success(self, sample_content):
        fp = FeedReader(
            "sample_url",
            request_agent=MockRequestAgent(content=sample_content),
            parser_agent=MockParserAgent(),
        )
        entries = fp.get_entries()
        assert isinstance(entries, list)
        assert len(entries) == 2
        assert all([isinstance(entry, Entry) for entry in entries])

    def test_get_entries_last_modified_success(self, sample_content):
        fp = FeedReader(
            "sample_url",
            request_agent=MockRequestAgent(content=sample_content),
            parser_agent=MockParserAgent(),
            last_modified=parse("2021-09-22 07:00 GMT"),
        )
        entries = fp.get_entries()
        assert isinstance(entries, list)
        assert len(entries) == 1
