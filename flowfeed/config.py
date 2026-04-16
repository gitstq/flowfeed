"""
Configuration management for FlowFeed.

Supports YAML config files and environment variables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


DEFAULT_CONFIG_PATH = Path.home() / ".flowfeed" / "config.yaml"


@dataclass
class SourceConfig:
    """Configuration for a single news source."""

    enabled: bool = True
    timeout: float = 15.0
    count: int = 30
    rate_limit: int = 300


@dataclass
class FilterConfig:
    """Keyword and regex filter configuration."""

    keywords: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)
    regex_include: str = ""
    regex_exclude: str = ""
    categories: list[str] = field(default_factory=list)
    min_hot_score: float = 0.0


@dataclass
class ExportConfig:
    """Export format configuration."""

    format: str = "terminal"  # terminal, json, markdown, html, rss
    output_dir: str = "./output"
    html_theme: str = "default"


@dataclass
class SchedulerConfig:
    """Scheduler configuration."""

    enabled: bool = False
    interval_minutes: int = 30
    sources: list[str] = field(default_factory=list)


@dataclass
class FlowFeedConfig:
    """Main configuration for FlowFeed."""

    sources: dict[str, SourceConfig] = field(default_factory=dict)
    filter: FilterConfig = field(default_factory=FilterConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)
    proxy: str = ""
    max_concurrent: int = 5
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )


def load_config(config_path: Optional[str | Path] = None) -> FlowFeedConfig:
    """Load configuration from YAML file, falling back to defaults."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not path.exists():
        return FlowFeedConfig()

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        return _parse_config(raw)
    except Exception as e:
        print(f"⚠️  Failed to load config from {path}: {e}")
        return FlowFeedConfig()


def _parse_config(raw: dict) -> FlowFeedConfig:
    """Parse raw dict into FlowFeedConfig."""
    cfg = FlowFeedConfig()

    # Sources
    if "sources" in raw:
        for src_id, src_raw in raw["sources"].items():
            if isinstance(src_raw, bool):
                cfg.sources[src_id] = SourceConfig(enabled=src_raw)
            elif isinstance(src_raw, dict):
                cfg.sources[src_id] = SourceConfig(
                    enabled=src_raw.get("enabled", True),
                    timeout=src_raw.get("timeout", 15.0),
                    count=src_raw.get("count", 30),
                    rate_limit=src_raw.get("rate_limit", 300),
                )

    # Filters
    if "filter" in raw:
        f = raw["filter"]
        cfg.filter = FilterConfig(
            keywords=f.get("keywords", []),
            exclude_keywords=f.get("exclude_keywords", []),
            regex_include=f.get("regex_include", ""),
            regex_exclude=f.get("regex_exclude", ""),
            categories=f.get("categories", []),
            min_hot_score=f.get("min_hot_score", 0.0),
        )

    # Export
    if "export" in raw:
        e = raw["export"]
        cfg.export = ExportConfig(
            format=e.get("format", "terminal"),
            output_dir=e.get("output_dir", "./output"),
            html_theme=e.get("html_theme", "default"),
        )

    # Scheduler
    if "scheduler" in raw:
        s = raw["scheduler"]
        cfg.scheduler = SchedulerConfig(
            enabled=s.get("enabled", False),
            interval_minutes=s.get("interval_minutes", 30),
            sources=s.get("sources", []),
        )

    # Global settings
    cfg.proxy = os.environ.get("FLOWFEED_PROXY", raw.get("proxy", ""))
    cfg.max_concurrent = raw.get("max_concurrent", 5)

    return cfg


def get_example_config() -> str:
    """Return example configuration as YAML string."""
    return """# FlowFeed Configuration Example
# Copy this file to ~/.flowfeed/config.yaml and modify as needed.

# Source configuration: enable/disable and customize each source
sources:
  weibo:        # 微博热搜
    enabled: true
    count: 30
    timeout: 15
  zhihu:        # 知乎热榜
    enabled: true
    count: 30
  baidu:        # 百度热搜
    enabled: true
    count: 30
  douyin:       # 抖音热搜
    enabled: true
    count: 30
  bilibili:     # B站热搜
    enabled: true
    count: 30
  hackernews:   # Hacker News
    enabled: true
    count: 30
  github:       # GitHub Trending
    enabled: true
    count: 30
  v2ex:         # V2EX
    enabled: true
    count: 20
  sspai:        # 少数派
    enabled: true
    count: 20
  thepaper:     # 澎湃新闻
    enabled: true
    count: 30
  zhihu_daily:  # 知乎日报
    enabled: true
    count: 10
  wechat:       # 微信热搜
    enabled: true
    count: 30
  headlines:    # 今日头条
    enabled: true
    count: 30
  netease:      # 网易新闻
    enabled: true
    count: 30
  weibo_search: # 微博搜索榜
    enabled: false
    count: 30
  producthunt:  # Product Hunt
    enabled: true
    count: 20

# Filter settings
filter:
  keywords: []              # Only show items containing these keywords
  exclude_keywords: []      # Exclude items containing these keywords
  regex_include: ""         # Regex pattern to include
  regex_exclude: ""         # Regex pattern to exclude
  categories: []            # Only show these categories
  min_hot_score: 0          # Minimum hot score threshold

# Export settings
export:
  format: "terminal"        # terminal | json | markdown | html | rss
  output_dir: "./output"
  html_theme: "default"

# Scheduler settings (requires: pip install flowfeed[scheduler])
scheduler:
  enabled: false
  interval_minutes: 30

# Global settings
proxy: ""                   # HTTP proxy, e.g. http://127.0.0.1:7890
max_concurrent: 5           # Max concurrent source fetches
"""
