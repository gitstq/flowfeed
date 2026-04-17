"""
Aggregation Engine — the core of FlowFeed.

Handles: parallel fetching, deduplication, sorting, filtering, and scoring.
"""

from __future__ import annotations

import asyncio
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from rich.console import Console

from flowfeed.config import FlowFeedConfig, SourceConfig
from flowfeed.i18n import t
from flowfeed.sources.base import FetchError, NewsItem, SourceBase

console = Console(stderr=True)


class AggregationResult:
    """Result of an aggregation run."""

    def __init__(self):
        self.items: list[NewsItem] = []
        self.errors: list[str] = []
        self.source_stats: dict[str, dict] = {}
        self.fetch_duration: float = 0.0
        self.total_fetched: int = 0
        self.total_after_dedup: int = 0
        self.total_after_filter: int = 0
        self.fetched_at: datetime = datetime.now(timezone.utc)

    def summary(self) -> str:
        lines = [
            f"📊 {t('engine.fetch_completed', dur=self.fetch_duration)}",
            f"   {t('engine.total_fetched', n=self.total_fetched)}",
            f"   {t('engine.after_dedup', n=self.total_after_dedup)}",
            f"   {t('engine.after_filter', n=self.total_after_filter)}",
            f"   {t('engine.sources_ok_fail', ok=len(self.source_stats), fail=len(self.errors))}",
        ]
        if self.errors:
            lines.append(f"   ❌ {t('engine.failed_sources')}")
            for err in self.errors[:5]:
                lines.append(f"      • {err}")
        return "\n".join(lines)


class AggregationEngine:
    """
    Core engine that orchestrates parallel fetching from multiple sources,
    deduplicates results, applies filters, and scores items.
    """

    def __init__(self, config: FlowFeedConfig):
        self.config = config

    async def aggregate(
        self,
        source_ids: Optional[list[str]] = None,
        count_per_source: int = 30,
    ) -> AggregationResult:
        """Run the full aggregation pipeline."""
        result = AggregationResult()
        start = time.monotonic()

        # Step 1: Select sources
        sources = self._select_sources(source_ids, count_per_source)

        if not sources:
            console.print(f"[yellow]⚠️  {t('engine.no_enabled_sources')}[/yellow]")
            return result

        # Step 2: Parallel fetch
        all_items, stats, errors = await self._parallel_fetch(sources)

        result.source_stats = stats
        result.errors = errors
        result.total_fetched = len(all_items)

        # Step 3: Deduplicate
        deduped = self._deduplicate(all_items)
        result.total_after_dedup = len(deduped)

        # Step 4: Filter
        filtered = self._filter(deduped)
        result.total_after_filter = len(filtered)

        # Step 5: Score and sort
        scored = self._score_and_sort(filtered)

        result.items = scored
        result.fetch_duration = time.monotonic() - start
        result.fetched_at = datetime.now(timezone.utc)

        console.print(result.summary())

        return result

    def _select_sources(
        self, source_ids: Optional[list[str]], count_per_source: int
    ) -> list[SourceBase]:
        """Select and instantiate source adapters based on config."""
        from flowfeed.sources import SOURCE_REGISTRY

        sources: list[SourceBase] = []

        if source_ids:
            target_ids = source_ids
        else:
            target_ids = list(SOURCE_REGISTRY.keys())

        for src_id in target_ids:
            if src_id not in SOURCE_REGISTRY:
                console.print(f"[yellow]⚠️  {t('engine.unknown_source', id=src_id)}[/yellow]")
                continue

            src_config = self.config.sources.get(src_id)
            if src_config and not src_config.enabled:
                continue

            cls = SOURCE_REGISTRY[src_id]
            timeout = src_config.timeout if src_config else 15.0
            count = src_config.count if src_config else count_per_source

            try:
                source = cls(timeout=timeout)
                sources.append(source)
            except Exception as e:
                console.print(f"[red]❌ {t('engine.init_source_failed', id=src_id, err=e)}[/red]")

        return sources

    async def _parallel_fetch(
        self, sources: list[SourceBase]
    ) -> tuple[list[NewsItem], dict[str, dict], list[str]]:
        """Fetch from all sources concurrently with error handling."""
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        all_items: list[NewsItem] = []
        stats: dict[str, dict] = {}
        errors: list[str] = []

        async def fetch_one(source: SourceBase) -> tuple[list[NewsItem], str, dict, Optional[str]]:
            try:
                async with semaphore:
                    console.print(f"📡 {t('engine.fetching_from', name=source.source_name)}")
                    items = await source.fetch(count=30)
                    console.print(f"   ✅ {t('engine.fetch_ok', name=source.source_name, n=len(items))}")
                    stat = {
                        "count": len(items),
                        "duration": "?",
                    }
                    return items, source.source_id, stat, None
            except FetchError as e:
                error_msg = f"{source.source_name}: HTTP {e.status_code}" if e.status_code else f"{source.source_name}: {e}"
                return [], source.source_id, {"count": 0, "error": str(e)}, error_msg
            except Exception as e:
                return [], source.source_id, {"count": 0, "error": str(e)}, f"{source.source_name}: {e}"

        tasks = [fetch_one(src) for src in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                errors.append(str(res))
                continue
            items, src_id, stat, error = res
            all_items.extend(items)
            stats[src_id] = stat
            if error:
                errors.append(error)

        return all_items, stats, errors

    def _deduplicate(self, items: list[NewsItem]) -> list[NewsItem]:
        """Remove duplicate items based on unique_key, keeping highest score."""
        seen: dict[str, NewsItem] = {}
        for item in items:
            key = item.unique_key
            if key not in seen or item.hot_score > seen[key].hot_score:
                seen[key] = item
        return list(seen.values())

    def _filter(self, items: list[NewsItem]) -> list[NewsItem]:
        """Apply keyword, regex, category, and score filters."""
        fc = self.config.filter
        if not fc.keywords and not fc.exclude_keywords and not fc.regex_include \
                and not fc.regex_exclude and not fc.categories and fc.min_hot_score <= 0:
            return items

        filtered: list[NewsItem] = []
        for item in items:
            # Category filter
            if fc.categories and item.category not in fc.categories:
                continue

            # Keyword include
            if fc.keywords:
                title_lower = item.title.lower()
                if not any(kw.lower() in title_lower for kw in fc.keywords):
                    continue

            # Keyword exclude
            if fc.exclude_keywords:
                title_lower = item.title.lower()
                if any(kw.lower() in title_lower for kw in fc.exclude_keywords):
                    continue

            # Regex include
            if fc.regex_include:
                if not re.search(fc.regex_include, item.title, re.IGNORECASE):
                    continue

            # Regex exclude
            if fc.regex_exclude:
                if re.search(fc.regex_exclude, item.title, re.IGNORECASE):
                    continue

            # Hot score threshold
            if item.hot_score < fc.min_hot_score:
                continue

            filtered.append(item)

        return filtered

    def _score_and_sort(self, items: list[NewsItem]) -> list[NewsItem]:
        """Normalize scores and sort by composite score."""
        if not items:
            return items

        # Normalize hot scores to 0-100 range per source
        source_scores: dict[str, list[float]] = defaultdict(list)
        for item in items:
            source_scores[item.source].append(item.hot_score)

        normalized: list[tuple[float, NewsItem]] = []
        for item in items:
            scores = source_scores[item.source]
            if not scores or max(scores) == 0:
                norm_score = 50.0
            else:
                norm_score = (item.hot_score / max(scores)) * 100

            # Composite score: normalized hot score + rank bonus
            rank_bonus = max(0, 100 - (item.rank * 2)) if item.rank > 0 else 50
            composite = norm_score * 0.7 + rank_bonus * 0.3

            normalized.append((composite, item))

        # Sort by composite score descending
        normalized.sort(key=lambda x: x[0], reverse=True)

        # Reassign ranks
        result: list[NewsItem] = []
        for i, (score, item) in enumerate(normalized):
            item.rank = i + 1
            item.hot_score = round(score, 2)
            result.append(item)

        return result
