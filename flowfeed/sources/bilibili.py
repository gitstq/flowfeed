"""Bilibili Hot Video source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class BilibiliHotSource(SourceBase):
    """Fetch trending videos from Bilibili."""

    source_id = "bilibili"
    source_name = "B站热搜"
    source_url = "https://www.bilibili.com"
    category = "social"
    description = "B站实时热搜榜"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://api.bilibili.com/x/web-interface/search/square",
                    params={"limit": str(count), "square": "1"},
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                trending = data.get("data", {}).get("trending", {}).get("list", [])
                for i, item in enumerate(trending[:count]):
                    keyword = item.get("keyword", "") or item.get("show_name", "")
                    if not keyword:
                        continue
                    url = f"https://search.bilibili.com/all?keyword={keyword}"
                    icon_name = item.get("icon_name", "")
                    items.append(NewsItem(
                        title=keyword,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=float(icon_name.replace("万", "0000")) if icon_name else 0.0,
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
            "Referer": "https://www.bilibili.com/",
        }
