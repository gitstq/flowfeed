"""Weibo Search Hot source adapter (微博搜索热词)."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class WeiboSearchSource(SourceBase):
    """Fetch hot search keywords from Weibo search trending."""

    source_id = "weibo_search"
    source_name = "微博搜索榜"
    source_url = "https://s.weibo.com"
    category = "social"
    description = "微博搜索实时热搜关键词"
    rate_limit_seconds = 180

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    "https://s.weibo.com/top/summary",
                    headers=self._headers(),
                    follow_redirects=True,
                )
                if resp.status_code == 200:
                    items = self._parse_html(resp.text, count)
        except httpx.RequestError:
            pass
        return items

    def _parse_html(self, html: str, count: int) -> list[NewsItem]:
        items: list[NewsItem] = []
        # Pattern for the trending list table
        tr_pattern = re.compile(
            r'<tr[^>]*>\s*<td[^>]*class="td-02"[^>]*>\s*<a[^>]*href="([^"]*)"[^>]*target="_blank"[^>]*>([^<]+)</a>'
            r'(?:(?:\s*<span[^>]*>([^<]*)</span>)?)',
            re.DOTALL,
        )
        for i, m in enumerate(tr_pattern.findall(html)[:count]):
            url_raw, title, extra = m
            title = title.strip()
            if not title:
                continue
            url = f"https://s.weibo.com{url_raw}" if url_raw.startswith("/") else url_raw
            hot_score = self._parse_number(extra) if extra else 0.0
            items.append(NewsItem(
                title=title,
                url=url,
                source=self.source_id,
                source_name=self.source_name,
                rank=i + 1,
                hot_score=hot_score,
                category=self.category,
            ))
        return items

    @staticmethod
    def _parse_number(s: str) -> float:
        s = s.strip()
        if not s:
            return 0.0
        m = re.search(r"([\d.]+)", s)
        if not m:
            return 0.0
        val = float(m.group(1))
        if "万" in s:
            val *= 10000
        return val

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html",
            "Referer": "https://weibo.com/",
        }
