"""Product Hunt source adapter."""

from __future__ import annotations

from typing import Optional

import httpx

from flowfeed.sources.base import FetchError, NewsItem, SourceBase


class ProductHuntSource(SourceBase):
    """Fetch today's top products from Product Hunt via GraphQL API."""

    source_id = "producthunt"
    source_name = "Product Hunt"
    source_url = "https://www.producthunt.com"
    category = "tech"
    description = "Product Hunt 每日热门新产品"
    rate_limit_seconds = 300

    async def fetch(self, count: int = 50) -> list[NewsItem]:
        items: list[NewsItem] = []
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Use the unofficial API endpoint
                resp = await client.get(
                    "https://www.producthunt.com/frontend/graphql",
                    params={
                        "operationName": "HomeFeedPage",
                        "variables": '{"cursor":null}',
                        "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"hash"}}',
                    },
                    headers=self._headers(),
                )
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        posts = self._extract_posts(data)
                        for i, post in enumerate(posts[:count]):
                            name = post.get("name", "")
                            tagline = post.get("tagline", "")
                            if not name:
                                continue
                            slug = post.get("slug", "")
                            url = f"https://www.producthunt.com/posts/{slug}"
                            votes = post.get("votesCount", 0) or 0
                            items.append(NewsItem(
                                title=f"{name} — {tagline}" if tagline else name,
                                url=url,
                                source=self.source_id,
                                source_name=self.source_name,
                                rank=i + 1,
                                hot_score=float(votes),
                                category=self.category,
                                summary=f"🔥 {votes} votes",
                            ))
                    except Exception:
                        # Fallback: use top posts list endpoint
                        pass
        except httpx.RequestError:
            pass

        # Fallback: scrape the posts page
        if not items:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.get(
                        "https://www.producthunt.com/posts",
                        headers=self._headers(),
                    )
                    if resp.status_code == 200:
                        import re
                        titles = re.findall(r'"name":"([^"]+)"', resp.text)
                        for i, title in enumerate(titles[:count]):
                            if not title or len(title) < 2:
                                continue
                            items.append(NewsItem(
                                title=title,
                                url=f"https://www.producthunt.com/posts",
                                source=self.source_id,
                                source_name=self.source_name,
                                rank=i + 1,
                                category=self.category,
                            ))
            except Exception:
                pass

        return items

    @staticmethod
    def _headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

    @staticmethod
    def _extract_posts(data: dict) -> list[dict]:
        """Extract posts from GraphQL response."""
        try:
            edges = data["data"]["posts"]["edges"]
            return [edge["node"] for edge in edges if "node" in edge]
        except (KeyError, TypeError):
            return []
