"""Toutiao (今日头条) source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class HeadlinesSource(SourceBase):
    """Fetch hot headlines from Toutiao (今日头条)."""

    source_id = "headlines"
    source_name = "今日头条"
    source_url = "https://www.toutiao.com"
    category = "news"
    description = "今日头条实时热榜"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://www.toutiao.com/hot-event/hot-board/",
                    params={"origin": "toutiao_pc"},
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                hot_list = data.get("data", [])
                for i, item in enumerate(hot_list[:count]):
                    title = item.get("Title", "")
                    if not title:
                        continue
                    url = item.get("Url", "")
                    items.append(NewsItem(
                        title=title,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=float(item.get("HotValue", 0) or 0),
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
            "Referer": "https://www.toutiao.com/",
            "Cookie": "tt_webid=1",
        }
