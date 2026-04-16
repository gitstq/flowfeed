"""Zhihu Hot List source adapter."""

from __future__ import annotations

from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class ZhihuHotSource(SourceBase):
    """Fetch trending topics from Zhihu Hot List."""

    source_id = "zhihu"
    source_name = "知乎热榜"
    source_url = "https://www.zhihu.com"
    category = "knowledge"
    description = "知乎实时热门问题榜"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total",
                    params={"limit": str(count)},
                    headers=self._headers(),
                )
                resp.raise_for_status()
                data = resp.json()
                for item_data in data.get("data", [])[:count]:
                    target = item_data.get("target", {})
                    title = target.get("title", "")
                    if not title:
                        continue
                    question_id = target.get("id", "")
                    url = f"https://www.zhihu.com/question/{question_id}"
                    excerpt = target.get("excerpt", "")
                    hot_score = float(item_data.get("detail_text", "0").replace("万热度", "0000").replace("热度", ""))
                    items.append(NewsItem(
                        title=title,
                        url=url,
                        source=self.source_id,
                        source_name=self.source_name,
                        hot_score=hot_score,
                        summary=excerpt[:200] if excerpt else "",
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
            "Referer": "https://www.zhihu.com/hot",
        }
