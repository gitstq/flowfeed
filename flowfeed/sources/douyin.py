"""Douyin Hot Video source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class DouyinHotSource(SourceBase):
    """Fetch trending videos from Douyin."""

    source_id = "douyin"
    source_name = "抖音热搜"
    source_url = "https://www.douyin.com"
    category = "social"
    description = "抖音实时热搜榜"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://www.douyin.com/aweme/v1/web/hot/search/list/",
                    headers=self._headers(),
                    params={"device_platform": "web", "aid": "6383", "count": str(count)},
                )
                resp.raise_for_status()
                data = resp.json()
                word_list = data.get("data", {}).get("word_list", [])
                for i, item in enumerate(word_list[:count]):
                    word = item.get("word", "")
                    if not word:
                        continue
                    event_time = item.get("event_time", 0)
                    url = f"https://www.douyin.com/search/{word}"
                    hot_score = float(item.get("hot_value", 0))
                    items.append(NewsItem(
                        title=word,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=hot_score,
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
            "Referer": "https://www.douyin.com/",
        }
