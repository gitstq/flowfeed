"""Zhihu Daily (知乎日报) source adapter."""

from __future__ import annotations

from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class ZhihuDailySource(SourceBase):
    """Fetch daily stories from Zhihu Daily."""

    source_id = "zhihu_daily"
    source_name = "知乎日报"
    source_url = "https://daily.zhihu.com"
    category = "knowledge"
    description = "知乎每日精选高质量文章"
    rate_limit_seconds = 3600

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Fetch today's stories
                resp = await client.get(
                    "https://news-at.zhihu.com/api/4/news/latest",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                stories = data.get("stories", [])
                for i, story in enumerate(stories[:count]):
                    title = story.get("title", "")
                    if not title:
                        continue
                    url = story.get("url", "")
                    story_id = story.get("id", "")
                    images = story.get("images", [])
                    items.append(NewsItem(
                        title=title,
                        url=url or f"https://daily.zhihu.com/story/{story_id}",
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        cover_url=images[0] if images else "",
                        category=self.category,
                    ))
        except httpx.HTTPStatusError as e:
            raise FetchError(self.source_id, f"HTTP {e.response.status_code}", e.response.status_code)
        except httpx.RequestError as e:
            raise FetchError(self.source_id, str(e))
        return items

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
