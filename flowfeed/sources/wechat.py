"""WeChat Hot Search source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class WeChatHotSource(SourceBase):
    """Fetch hot search from WeChat (微信热搜)."""

    source_id = "wechat"
    source_name = "微信热搜"
    source_url = "https://weixin.sogou.com"
    category = "social"
    description = "微信热搜榜"
    rate_limit_seconds = 300

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use Sogou WeChat search hot list
                resp = await client.get(
                    "https://weixin.sogou.com/pcindex/pc/pc_0/pc_0.html",
                    headers=self._headers(),
                    follow_redirects=True,
                )
                if resp.status_code == 200:
                    items = self._parse_html(resp.text, count)
        except httpx.RequestError:
            pass

        # Fallback: try the API
        if not items:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        "https://tenapi.cn/v2/weixinhot",
                        headers=self._headers(),
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        news_list = data.get("data", [])
                        for i, item in enumerate(news_list[:count]):
                            title = item.get("name", "") or item.get("title", "")
                            if not title:
                                continue
                            items.append(NewsItem(
                                title=title,
                                url=item.get("url", ""),
                                source=self.source_id,
                                source_name=self.source_name,
                                rank=i + 1,
                                hot_score=float(item.get("hot", 0) or 0),
                                category=self.category,
                            ))
            except Exception:
                pass

        return items

    def _parse_html(self, html: str, count: int) -> list[NewsItem]:
        items: list[NewsItem] = []
        pattern = re.compile(r'<p[^>]*class="rt_news"[^>]*>\s*<a[^>]*>([^<]+)</a>', re.DOTALL)
        for i, m in enumerate(pattern.findall(html)[:count]):
            title = m.strip()
            if title:
                items.append(NewsItem(
                    title=title,
                    url=f"https://weixin.sogou.com/weixin?type=2&query={title}",
                    source=self.source_id,
                    source_name=self.source_name,
                    rank=i + 1,
                    category=self.category,
                ))
        return items

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html",
            "Referer": "https://weixin.sogou.com/",
        }
