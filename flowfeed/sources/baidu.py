"""Baidu Hot Search source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class BaiduHotSource(SourceBase):
    """Fetch trending topics from Baidu Hot Search."""

    source_id = "baidu"
    source_name = "百度热搜"
    source_url = "https://www.baidu.com"
    category = "general"
    description = "百度实时热搜榜"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://top.baidu.com/api/board?platform=wise&tab=realtime",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                cards = data.get("data", {}).get("cards", [])
                for card in cards:
                    for i, item in enumerate(card.get("content", [])[:count]):
                        query = item.get("query", "") or item.get("word", "")
                        if not query:
                            continue
                        desc = item.get("desc", "")
                        url = f"https://www.baidu.com/s?wd={query}"
                        hot_score = self._parse_hot(item.get("hotScore", "0"))
                        items.append(NewsItem(
                            title=query,
                            url=url,
                            source=self.source_id,
                            source_name=self.source_name,
                            rank=i + 1,
                            hot_score=hot_score,
                            summary=desc[:200] if desc else "",
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
            "Referer": "https://www.baidu.com/",
        }

    @staticmethod
    def _parse_hot(score_str) -> float:
        """Parse hot score like '4987234' or '4.9万'."""
        s = str(score_str)
        m = re.search(r"([\d.]+)\s*万?", s)
        if not m:
            return 0.0
        val = float(m.group(1))
        if "万" in s:
            val *= 10000
        return val
