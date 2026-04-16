"""NetEase (网易新闻) source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class NeteaseSource(SourceBase):
    """Fetch hot news from Netease (网易新闻)."""

    source_id = "netease"
    source_name = "网易新闻"
    source_url = "https://news.163.com"
    category = "news"
    description = "网易新闻实时热榜"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://m.163.com/nc/article/headline/T1348647853363/0-40.html",
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                news_list = data.get("T1348647853363", [])
                for i, item in enumerate(news_list[:count]):
                    title = item.get("title", "")
                    if not title:
                        continue
                    docid = item.get("docid", "")
                    url = item.get("url", "") or f"https://www.163.com/news/article/{docid}.html"
                    digest = item.get("digest", "")
                    items.append(NewsItem(
                        title=title,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=float(item.get("replyCount", 0) or 0) * 10,
                        summary=digest[:200] if digest else "",
                        category=item.get("channel", "") or self.category,
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
            "Referer": "https://news.163.com/",
        }
