import logging
import typing

import feedparser
import requests
from datetime import datetime
from dateutil.parser import parse

from feedreader.entities import Feed, Entry
from feedreader.exceptions import FeedReaderBaseException, UnSuccessfulRequestException


logger = logging.getLogger(__name__)


class FeedReader:
    def __init__(
        self,
        url,
        request_agent=None,
        parser_agent=None,
        last_modified: datetime = None,
        timeout: int = 5,
    ):
        self._url = url
        self._request_agent = request_agent if request_agent else requests
        self._parser_agent = parser_agent if parser_agent else feedparser
        self._last_modified = last_modified
        self._timeout = timeout

    def get_feed_info(self) -> Feed:
        self._fetch()
        self._validate()
        return self._handle_feed_info()

    def get_entries(self) -> typing.List[Entry]:
        self._fetch()
        self._validate()
        return self._handle_entries()

    def _fetch(self):
        if not hasattr(self, "data"):
            resp = self._request_agent.get(
                self._url,
                timeout=self._timeout,
                headers={
                    "If-Modified-Since": self._last_modified.strftime(
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                    if self._last_modified
                    else None
                },
            )
            if resp.status_code not in (200, 304):
                raise UnSuccessfulRequestException(
                    f"Resp with status code {resp.status_code}"
                )
            self.data = self._parser_agent.parse(resp.content)

    def _validate(self):
        if self.data.bozo:
            logger.error(self.data.bozo_exception)
            raise FeedReaderBaseException(self.data.bozo_exception)

    def _handle_entries(self) -> typing.List[Entry]:
        entries_list = []
        for entry in self.data.entries:
            published_at = parse(entry["published"])
            if self._last_modified and published_at <= self._last_modified:
                break
            entries_list.append(
                Entry(
                    title=entry["title"],
                    url=entry["link"],
                    summary=entry["summary"],
                    published_at=published_at,
                )
            )
        return entries_list

    def _handle_feed_info(self):
        if self.data.feed:
            return Feed(
                title=self.data.feed["title"],
                url=self._url,
            )
        return None
