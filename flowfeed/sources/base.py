"""
Base classes and data models for news sources.

Every source adapter must inherit from SourceBase and implement
the fetch() method returning a list of NewsItem.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class NewsItem:
    """A single news item from any source."""

    title: str
    url: str
    source: str  # source_id, e.g. "weibo", "zhihu"
    source_name: str  # human-readable name, e.g. "微博热搜"
    rank: int = 0
    hot_score: float = 0.0
    category: str = ""
    summary: str = ""
    cover_url: str = ""
    author: str = ""
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def unique_key(self) -> str:
        """Generate a deduplication key based on title + source."""
        raw = f"{self.source}:{self.title.strip()}"
        return hashlib.md5(raw.encode("utf-8", errors="ignore")).hexdigest()

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "source": self.source,
            "source_name": self.source_name,
            "rank": self.rank,
            "hot_score": self.hot_score,
            "category": self.category,
            "summary": self.summary,
            "cover_url": self.cover_url,
            "author": self.author,
            "fetched_at": self.fetched_at.isoformat(),
        }


class SourceBase:
    """Abstract base class for all news source adapters."""

    source_id: str = ""
    source_name: str = ""
    source_url: str = ""
    category: str = "general"
    description: str = ""
    rate_limit_seconds: int = 300  # default: 5 minutes

    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        """
        Fetch news items from this source.

        Args:
            count: Maximum number of items to return.

        Returns:
            List of NewsItem objects.

        Raises:
            FetchError: If fetching fails.
        """
        raise NotImplementedError

    @classmethod
    def is_available(cls) -> bool:
        """Check if this source is available (e.g., dependencies met)."""
        return True


class FetchError(Exception):
    """Raised when a source fetch fails."""

    def __init__(self, source: str, message: str, status_code: Optional[int] = None):
        self.source = source
        self.status_code = status_code
        super().__init__(f"[{source}] {message}")
