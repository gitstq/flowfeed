"""V2EX source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class V2EXSource(SourceBase):
    """Fetch latest hot topics from V2EX."""

    source_id = "v2ex"
    source_name = "V2EX"
    source_url = "https://www.v2ex.com"
    category = "tech"
    description = "V2EX 创意工作者社区热帖"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://www.v2ex.com/api/topics/hot.json",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                for i, topic in enumerate(data[:count]):
                    title = topic.get("title", "")
                    if not title:
                        continue
                    url = topic.get("url", "")
                    replies = topic.get("replies", 0) or 0
                    node = topic.get("node", {})
                    node_name = node.get("name", "") if node else ""
                    member = topic.get("member", {})
                    author = member.get("username", "") if member else ""
                    items.append(NewsItem(
                        title=title,
                        url=f"https://www.v2ex.com{url}" if url.startswith("/") else url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=float(replies) * 10,
                        author=author,
                        category=node_name or self.category,
                    ))
        except httpx.HTTPStatusError as e:
            raise FetchError(self.source_id, f"HTTP {e.response.status_code}", e.response.status_code)
        except httpx.RequestError as e:
            raise FetchError(self.source_id, str(e))
        return items

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "FlowFeed/1.0 (news aggregator)",
            "Accept": "application/json",
        }
