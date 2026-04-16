"""Sspai (少数派) source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class SspaiSource(SourceBase):
    """Fetch trending articles from Sspai (少数派)."""

    source_id = "sspai"
    source_name = "少数派"
    source_url = "https://sspai.com"
    category = "tech"
    description = "少数派高质量科技生活文章"
    rate_limit_seconds = 300

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://sspai.com/api/v1/article/topic/page/get",
                    params={"limit": str(count), "offset": "0", "created_at": "0"},
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                articles = data.get("data", [])
                for i, article in enumerate(articles[:count]):
                    title = article.get("title", "")
                    if not title:
                        continue
                    article_id = article.get("id", "")
                    desc = article.get("desc", "")
                    author_info = article.get("author", {})
                    author = author_info.get("nickname", "") if author_info else ""
                    items.append(NewsItem(
                        title=title,
                        url=f"https://sspai.com/post/{article_id}",
                        source=self.source_id,
                        source_name=self.source_name,
                        rank=i + 1,
                        hot_score=float(article.get("like_count", 0) or 0) + float(article.get("comment_count", 0) or 0) * 5,
                        summary=desc[:200] if desc else "",
                        author=author,
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
            "Referer": "https://sspai.com/",
        }
