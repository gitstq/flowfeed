"""Weibo Hot Search source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class WeiboHotSource(SourceBase):
    """Fetch trending topics from Weibo Hot Search."""

    source_id = "weibo"
    source_name = "微博热搜"
    source_url = "https://weibo.com"
    category = "social"
    description = "微博实时热搜榜"
    rate_limit_seconds = 120

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://weibo.com/ajax/side/hotSearch",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                realtime = data.get("data", {}).get("realtime", [])
                for i, item in enumerate(realtime[:count]):
                    word = item.get("word", "")
                    if not word:
                        continue
                    note = item.get("note", "") or word
                    url = f"https://s.weibo.com/weibo?q=%23{word}%23"
                    hot_score = self._parse_hot_score(item.get("num", 0))
                    items.append(NewsItem(
                        title=note,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=hot_score,
                        category=self._detect_category(note),
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
            "Referer": "https://weibo.com/",
        }

    @staticmethod
    def _parse_hot_score(num) -> float:
        if isinstance(num, (int, float)):
            return float(num)
        if isinstance(num, str):
            m = re.search(r"([\d.]+)", num)
            return float(m.group(1)) if m else 0.0
        return 0.0

    @staticmethod
    def _detect_category(title: str) -> str:
        keywords = {
            "影视": "entertainment",
            "综艺": "entertainment",
            "明星": "entertainment",
            "电影": "entertainment",
            "音乐": "entertainment",
            "科技": "tech",
            "AI": "tech",
            "芯片": "tech",
            "手机": "tech",
            "股市": "finance",
            "经济": "finance",
            "楼市": "finance",
            "体育": "sports",
            "足球": "sports",
            "篮球": "sports",
        }
        for kw, cat in keywords.items():
            if kw in title:
                return cat
        return "general"
