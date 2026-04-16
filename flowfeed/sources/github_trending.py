"""GitHub Trending source adapter."""

from __future__ import annotations

import re
from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class GitHubTrendingSource(SourceBase):
    """Fetch trending repositories from GitHub."""

    source_id = "github"
    source_name = "GitHub Trending"
    source_url = "https://github.com/trending"
    category = "tech"
    description = "GitHub 每日热门开源项目"
    rate_limit_seconds = 300

    def __init__(self, timeout: float = 20.0, language: str = ""):
        super().__init__(timeout)
        self.language = language

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                url = "https://github.com/trending"
                if self.language:
                    url += f"/{self.language}"
                resp = await client.get(url, headers=self._headers())
                resp.raise_for_status()
                # Parse HTML
                items = self._parse_html(resp.text, count)
        except httpx.HTTPStatusError as e:
            raise FetchError(self.source_id, f"HTTP {e.response.status_code}", e.response.status_code)
        except httpx.RequestError as e:
            raise FetchError(self.source_id, str(e))
        return items

    def _parse_html(self, html: str, count: int) -> list[NewsItem]:
        items: list[NewsItem] = []
        # Pattern for repo entries
        repo_pattern = re.compile(
            r'<h2[^>]*class="[^"]*h3[^"]*"[^>]*>\s*'
            r'<a[^>]*href="(/[^"]+)"[^>]*>\s*([^<\s][^<]*)\s*/\s*([^<]+)\s*</a>',
            re.DOTALL,
        )
        desc_pattern = re.compile(
            r'<p[^>]*class="[^"]*color-fg-muted[^"]*"[^>]*>([^<]+)</p>',
            re.DOTALL,
        )
        star_pattern = re.compile(
            r'<svg[^>]*octicon-star[^>]*>.*?</svg>\s*([\d,]+)',
            re.DOTALL,
        )
        today_stars_pattern = re.compile(
            r'([\d,]+)\s*stars\s*today',
            re.IGNORECASE | re.DOTALL,
        )

        repos = repo_pattern.findall(html)
        for i, (path, owner, repo) in enumerate(repos[:count]):
            # Find description in surrounding context
            full_name = f"{owner.strip()}/{repo.strip()}"
            desc_match = desc_pattern.search(html[html.find(path):][:500] if path in html else html)
            desc = desc_match.group(1).strip() if desc_match else ""

            # Find star counts
            context = html[html.find(path):][:1000] if path in html else ""
            star_match = star_pattern.search(context)
            today_match = today_stars_pattern.search(context)
            total_stars = self._parse_number(star_match.group(1)) if star_match else 0
            today_stars = self._parse_number(today_match.group(1)) if today_match else 0

            items.append(NewsItem(
                title=full_name,
                url=f"https://github.com{path}",
                source=self.source_id,
                source_name=self.source_name,
                rank=i + 1,
                hot_score=float(today_stars * 100 + total_stars),
                category=self.language if self.language else self.category,
                summary=desc[:200] if desc else f"⭐ {total_stars:,}  🌟 today: +{today_stars:,}",
            ))
        return items

    @staticmethod
    def _parse_number(s: str) -> int:
        return int(s.replace(",", "").replace(".", "").strip() or "0")

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html",
            "Accept-Language": "en-US,en;q=0.9",
        }
