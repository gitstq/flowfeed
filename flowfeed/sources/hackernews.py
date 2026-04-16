"""Hacker News source adapter."""

from __future__ import annotations

from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class HackerNewsSource(SourceBase):
    """Fetch top stories from Hacker News (Algolia API)."""

    source_id = "hackernews"
    source_name = "Hacker News"
    source_url = "https://news.ycombinator.com"
    category = "tech"
    description = "Hacker News 热门技术讨论"
    rate_limit_seconds = 60

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={
                        "tags": "story",
                        "hitsPerPage": str(count),
                    },
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                for i, hit in enumerate(data.get("hits", [])[:count]):
                    title = hit.get("title", "")
                    if not title:
                        continue
                    url = hit.get("url", "") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                    points = hit.get("points", 0) or 0
                    num_comments = hit.get("num_comments", 0) or 0
                    author = hit.get("author", "")
                    items.append(NewsItem(
                        title=title,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=float(points) + float(num_comments) * 2,
                        author=author,
                        category=self.category,
                        summary=f"▲ {points}  💬 {num_comments}",
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
