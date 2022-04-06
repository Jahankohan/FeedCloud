from dataclasses import dataclass

from datetime import datetime


@dataclass
class Feed:
    title: str
    url: str


@dataclass
class Entry:
    title: str
    url: str
    summary: str
    published_at: datetime
