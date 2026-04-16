"""The Paper (澎湃新闻) source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class ThePaperSource(SourceBase):
    """Fetch hot news from The Paper (澎湃新闻)."""

    source_id = "thepaper"
    source_name = "澎湃新闻"
    source_url = "https://www.thepaper.cn"
    category = "news"
    description = "澎湃新闻实时热榜"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                hot_news = data.get("data", {}).get("hotNews", [])
                for i, item in enumerate(hot_news[:count]):
                    title = item.get("name", "")
                    if not title:
                        continue
                    cont_id = item.get("contId", "")
                    url = f"https://www.thepaper.cn/newsDetail_forward_{cont_id}"
                    items.append(NewsItem(
                        title=title,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
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
            "Referer": "https://www.thepaper.cn/",
        }
