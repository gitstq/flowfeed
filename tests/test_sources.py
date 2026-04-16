"""Tests for FlowFeed."""

import asyncio
import json
from pathlib import Path

from flowfeed.config import FlowFeedConfig, FilterConfig, load_config
from flowfeed.engine import AggregationEngine, AggregationResult
from flowfeed.sources.base import NewsItem, SourceBase
from flowfeed.exporters.json_export import JSONExporter
from flowfeed.exporters.markdown import MarkdownExporter
from flowfeed.exporters.rss import RSSExporter


class TestNewsItem:
    """Test NewsItem data model."""

    def test_create(self):
        item = NewsItem(
            title="Test Title",
            url="https://example.com",
            source="test",
            source_name="Test Source",
        )
        assert item.title == "Test Title"
        assert item.url == "https://example.com"
        assert item.source == "test"

    def test_unique_key(self):
        item1 = NewsItem(title="Hello World", source="test", source_name="Test")
        item2 = NewsItem(title="Hello World", source="test", source_name="Test")
        item3 = NewsItem(title="Different", source="test", source_name="Test")

        assert item1.unique_key == item2.unique_key
        assert item1.unique_key != item3.unique_key

    def test_to_dict(self):
        item = NewsItem(
            title="Test",
            url="https://example.com",
            source="test",
            source_name="Test Source",
            rank=1,
            hot_score=99.5,
        )
        d = item.to_dict()
        assert d["title"] == "Test"
        assert d["rank"] == 1
        assert d["hot_score"] == 99.5


class TestSourceRegistry:
    """Test that all sources are properly registered."""

    def test_all_sources_registered(self):
        from flowfeed.sources import ALL_SOURCES, SOURCE_REGISTRY
        assert len(ALL_SOURCES) >= 16
        assert len(SOURCE_REGISTRY) == len(ALL_SOURCES)

    def test_source_has_required_attributes(self):
        from flowfeed.sources import ALL_SOURCES
        for cls in ALL_SOURCES:
            assert cls.source_id, f"{cls.__name__} missing source_id"
            assert cls.source_name, f"{cls.__name__} missing source_name"
            assert cls.category, f"{cls.__name__} missing category"

    def test_no_duplicate_source_ids(self):
        from flowfeed.sources import ALL_SOURCES
        ids = [cls.source_id for cls in ALL_SOURCES]
        assert len(ids) == len(set(ids)), "Duplicate source IDs found"


class TestEngine:
    """Test aggregation engine logic."""

    def test_deduplication(self):
        from flowfeed.engine import AggregationEngine
        engine = AggregationEngine(FlowFeedConfig())

        items = [
            NewsItem(title="Same Title", url="https://x.com", source="test", source_name="Test", hot_score=10),
            NewsItem(title="Same Title", url="https://x.com", source="test", source_name="Test", hot_score=20),
            NewsItem(title="Different", url="https://y.com", source="test", source_name="Test", hot_score=5),
        ]

        result = engine._deduplicate(items)
        assert len(result) == 2
        same_item = [i for i in result if i.title == "Same Title"][0]
        assert same_item.hot_score == 20

    def test_filter_keywords(self):
        from flowfeed.engine import AggregationEngine
        config = FlowFeedConfig()
        config.filter.keywords = ["AI"]
        engine = AggregationEngine(config)

        items = [
            NewsItem(title="AI is amazing", url="https://a.com", source="test", source_name="Test"),
            NewsItem(title="Unrelated news", url="https://b.com", source="test", source_name="Test"),
            NewsItem(title="New AI model released", url="https://c.com", source="test", source_name="Test"),
        ]

        result = engine._filter(items)
        assert len(result) == 2

    def test_filter_exclude(self):
        from flowfeed.engine import AggregationEngine
        config = FlowFeedConfig()
        config.filter.exclude_keywords = ["ad"]
        engine = AggregationEngine(config)

        items = [
            NewsItem(title="Important news", url="https://a.com", source="test", source_name="Test"),
            NewsItem(title="Click this ad now", url="https://b.com", source="test", source_name="Test"),
        ]

        result = engine._filter(items)
        assert len(result) == 1
        assert result[0].title == "Important news"

    def test_filter_min_score(self):
        from flowfeed.engine import AggregationEngine
        config = FlowFeedConfig()
        config.filter.min_hot_score = 50.0
        engine = AggregationEngine(config)

        items = [
            NewsItem(title="Low", url="https://a.com", source="test", source_name="Test", hot_score=10),
            NewsItem(title="High", url="https://b.com", source="test", source_name="Test", hot_score=100),
            NewsItem(title="Medium", url="https://c.com", source="test", source_name="Test", hot_score=50),
        ]

        result = engine._filter(items)
        assert len(result) == 2

    def test_score_and_sort(self):
        from flowfeed.engine import AggregationEngine
        engine = AggregationEngine(FlowFeedConfig())

        items = [
            NewsItem(title="C", url="https://c.com", source="test", source_name="Test", hot_score=10, rank=3),
            NewsItem(title="A", url="https://a.com", source="test", source_name="Test", hot_score=100, rank=1),
            NewsItem(title="B", url="https://b.com", source="test", source_name="Test", hot_score=50, rank=2),
        ]

        result = engine._score_and_sort(items)
        assert len(result) == 3
        assert result[0].title == "A"
        assert result[0].rank == 1


class TestExporters:
    """Test export functionality."""

    def test_json_export(self):
        items = [
            NewsItem(title="Test 1", url="https://example.com/1", source="test", source_name="Test", rank=1),
            NewsItem(title="Test 2", url="https://example.com/2", source="test", source_name="Test", rank=2),
        ]

        exporter = JSONExporter()
        result = exporter.export(items, pretty=True)
        data = json.loads(result)
        assert data["total"] == 2
        assert data["items"][0]["title"] == "Test 1"

    def test_markdown_export(self):
        items = [
            NewsItem(title="Test", url="https://example.com", source="test", source_name="Test", rank=1),
        ]

        exporter = MarkdownExporter()
        result = exporter.export(items)
        assert "# " in result
        assert "Test" in result
        assert "https://example.com" in result

    def test_rss_export(self):
        items = [
            NewsItem(title="Test", url="https://example.com", source="test", source_name="Test", rank=1),
        ]

        exporter = RSSExporter()
        result = exporter.export(items)
        assert '<?xml version' in result
        assert '<rss' in result
        assert '<item>' in result

    def test_html_export(self):
        items = [
            NewsItem(title="Test", url="https://example.com", source="test", source_name="Test", rank=1, hot_score=50),
        ]

        from flowfeed.exporters.html_report import HTMLReportExporter
        exporter = HTMLReportExporter()
        result = exporter.export(items)
        assert '<!DOCTYPE html>' in result
        assert 'FlowFeed' in result
        assert 'Test' in result


class TestConfig:
    """Test configuration management."""

    def test_default_config(self):
        config = FlowFeedConfig()
        assert config.filter.keywords == []
        assert config.export.format == "terminal"
        assert config.max_concurrent == 5

    def test_example_config_generation(self):
        from flowfeed.config import get_example_config
        config_str = get_example_config()
        assert "weibo" in config_str
        assert "hackernews" in config_str
        assert "filter" in config_str
