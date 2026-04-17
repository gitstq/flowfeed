"""
FlowFeed CLI — Command-line interface.

Usage:
    flowfeed                    # Fetch all sources, display in terminal
    flowfeed --source weibo zhihu hackernews
    flowfeed --format json -o output.json
    flowfeed --format html -o dashboard.html
    flowfeed --format markdown -o digest.md
    flowfeed --format rss -o feed.xml
    flowfeed --filter-keyword AI 人工智能
    flowfeed --exclude-keyword 广告
    flowfeed --category tech social
    flowfeed --limit 100
    flowfeed list-sources        # List all available sources
    flowfeed init-config         # Generate example config file
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flowfeed import __version__
from flowfeed.config import (
    DEFAULT_CONFIG_PATH,
    FlowFeedConfig,
    get_example_config,
    load_config,
)
from flowfeed.engine import AggregationEngine
from flowfeed.exporters import (
    HTMLReportExporter,
    JSONExporter,
    MarkdownExporter,
    RSSExporter,
    TerminalExporter,
)
from flowfeed.i18n import SUPPORTED_LOCALES, detect_locale, set_locale, t
from flowfeed.sources import ALL_SOURCES, SOURCE_REGISTRY

console = Console()


def _get_config(config_path: Optional[str]) -> FlowFeedConfig:
    return load_config(config_path)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="flowfeed")
@click.option("-c", "--config", "config_path", default=None, help="Path to config YAML file.")
@click.option("-s", "--source", "sources", multiple=True, help="Specific source IDs to fetch.")
@click.option("-f", "--format", "fmt", default="terminal", type=click.Choice(["terminal", "json", "markdown", "html", "rss"]), help="Output format.")
@click.option("-o", "--output", default=None, help="Output file path.")
@click.option("-n", "--limit", default=50, type=int, help="Max items to show per source.")
@click.option("-l", "--lang", "lang", default="", type=click.Choice(["", "en", "zh-CN", "zh-TW"]), help="UI language (en, zh-CN, zh-TW). Default: auto-detect.")
@click.option("--filter-keyword", "keywords", multiple=True, help="Only show items containing these keywords.")
@click.option("--exclude-keyword", "exclude_keywords", multiple=True, help="Exclude items containing these keywords.")
@click.option("--regex-include", default="", help="Regex pattern to include items.")
@click.option("--regex-exclude", default="", help="Regex pattern to exclude items.")
@click.option("--category", "categories", multiple=True, help="Only show items in these categories.")
@click.option("--min-score", default=0, type=float, help="Minimum hot score threshold.")
@click.option("--proxy", default="", help="HTTP proxy URL.")
@click.pass_context
def main(
    ctx: click.Context,
    config_path: Optional[str],
    sources: tuple[str, ...],
    fmt: str,
    output: Optional[str],
    limit: int,
    lang: str,
    keywords: tuple[str, ...],
    exclude_keywords: tuple[str, ...],
    regex_include: str,
    regex_exclude: str,
    categories: tuple[str, ...],
    min_score: float,
    proxy: str,
) -> None:
    """FlowFeed — Lightweight Intelligent News Aggregation Engine 📡"""
    # Initialize i18n for all commands (main + subcommands)
    if lang:
        set_locale(lang)
    else:
        cfg = load_config(config_path)
        if cfg.language:
            set_locale(cfg.language)
        else:
            set_locale(detect_locale())

    if ctx.invoked_subcommand:
        return

    # Load config and apply CLI overrides
    config = _get_config(config_path)

    if keywords:
        config.filter.keywords = list(keywords)
    if exclude_keywords:
        config.filter.exclude_keywords = list(exclude_keywords)
    if regex_include:
        config.filter.regex_include = regex_include
    if regex_exclude:
        config.filter.regex_exclude = regex_exclude
    if categories:
        config.filter.categories = list(categories)
    if min_score > 0:
        config.filter.min_hot_score = min_score
    if proxy:
        config.proxy = proxy

    # Set export format
    config.export.format = fmt
    if output:
        config.export.output_dir = str(Path(output).parent)

    # Run aggregation
    source_list = list(sources) if sources else None

    try:
        result = asyncio.run(_run_fetch(config, source_list, limit, fmt, output))
    except KeyboardInterrupt:
        console.print(f"\n[yellow]{t('cli.interrupted')}[/yellow]")
        sys.exit(1)


async def _run_fetch(
    config: FlowFeedConfig,
    source_ids: Optional[list[str]],
    limit: int,
    fmt: str,
    output: Optional[str],
) -> None:
    """Run the fetch → export pipeline."""
    engine = AggregationEngine(config)
    result = await engine.aggregate(source_ids=source_ids, count_per_source=limit)

    if not result.items:
        console.print(f"[yellow]{t('cli.no_items')}[/yellow]")
        return

    # Export
    if fmt == "terminal":
        exporter = TerminalExporter()
        exporter.export(result.items)
    elif fmt == "json":
        exporter = JSONExporter()
        exporter.export(result.items, output=output or "flowfeed_output.json")
        console.print(f"[green]✅ {t('export.to_json', n=len(result.items))}[/green]")
    elif fmt == "markdown":
        exporter = MarkdownExporter()
        exporter.export(result.items, output=output or "flowfeed_digest.md")
        console.print(f"[green]✅ {t('export.to_markdown', n=len(result.items))}[/green]")
    elif fmt == "html":
        exporter = HTMLReportExporter()
        exporter.export(result.items, output=output or "flowfeed_dashboard.html")
        console.print(f"[green]✅ {t('export.to_html', n=len(result.items))}[/green]")
    elif fmt == "rss":
        exporter = RSSExporter()
        exporter.export(result.items, output=output or "flowfeed_feed.xml")
        console.print(f"[green]✅ {t('export.to_rss', n=len(result.items))}[/green]")


@main.command("list-sources")
def list_sources_cmd() -> None:
    """List all available news sources."""
    table = Table(title=f"📡 {t('cli.list_sources.title')}", show_header=True, header_style="bold cyan")
    table.add_column(t("cli.list_sources.col_id"), style="cyan", width=16)
    table.add_column(t("cli.list_sources.col_name"), style="bold white", min_width=12)
    table.add_column(t("cli.list_sources.col_category"), style="green", width=12)
    table.add_column(t("cli.list_sources.col_description"), style="dim", min_width=30)

    for cls in ALL_SOURCES:
        table.add_row(
            cls.source_id,
            cls.source_name,
            cls.category,
            cls.description,
        )

    console.print(table)
    console.print(f"\n[dim]{t('cli.list_sources.total', n=len(ALL_SOURCES))}[/dim]")


@main.command("init-config")
@click.option("--path", "config_path", default=None, help="Custom config file path.")
def init_config_cmd(config_path: Optional[str]) -> None:
    """Generate an example configuration file."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        if not click.confirm(t("cli.init_config.exists", path=path)):
            console.print(f"[yellow]{t('cli.init_config.cancelled')}[/yellow]")
            return

    example = get_example_config()
    path.write_text(example, encoding="utf-8")
    console.print(f"[green]✅ {t('cli.init_config.written', path=path)}[/green]")
    console.print(f"[dim]{t('cli.init_config.hint')}[/dim]")


@main.command("sources")
def show_sources() -> None:
    """Show source IDs for use with --source flag."""
    for cls in ALL_SOURCES:
        status = "✅" if cls.is_available() else "❌"
        console.print(f"  {status} [cyan]{cls.source_id:<16}[/cyan] {cls.source_name} ({cls.category})")


if __name__ == "__main__":
    main()
