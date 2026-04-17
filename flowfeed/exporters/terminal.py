"""Terminal (Rich) output exporter."""

from __future__ import annotations

from typing import TextIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from flowfeed.i18n import t
from flowfeed.sources.base import NewsItem


class TerminalExporter:
    """Export news items to a beautifully formatted terminal table."""

    def __init__(self, console: Console | None = None, file: TextIO | None = None):
        self.console = console or Console(file=file)

    def export(self, items: list[NewsItem], title: str = "FlowFeed 📡") -> None:
        if not items:
            self.console.print(f"[yellow]{t('term.no_items')}[/yellow]")
            return

        # Group by source
        by_source: dict[str, list[NewsItem]] = {}
        for item in items:
            by_source.setdefault(item.source_name, []).append(item)

        # Header
        self.console.print()
        self.console.print(
            Panel(
                f"[bold cyan]🔥 FlowFeed[/bold cyan] — {t('term.header', items=len(items), sources=len(by_source))}\n"
                f"[dim]{t('term.header_sub')}[/dim]",
                border_style="cyan",
            )
        )

        # Full ranking table
        self._render_full_table(items)

        # Per-source summary
        self._render_source_summary(by_source)

    def _render_full_table(self, items: list[NewsItem], limit: int = 50) -> None:
        table = Table(
            title=f"📋 {t('term.top_stories')}",
            show_header=True,
            header_style="bold magenta",
            border_style="dim",
            title_style="bold",
        )
        table.add_column(t("term.col_rank"), style="dim", width=4, justify="right")
        table.add_column(t("term.col_score"), style="yellow", width=6, justify="right")
        table.add_column(t("term.col_title"), style="bold white", min_width=40, no_wrap=False)
        table.add_column(t("term.col_source"), style="cyan", width=14)
        table.add_column(t("term.col_category"), style="green", width=12)

        for item in items[:limit]:
            # Truncate title for display
            title = item.title[:60] + "..." if len(item.title) > 60 else item.title
            cat = item.category if item.category else "—"
            table.add_row(
                str(item.rank),
                f"{item.hot_score:.0f}",
                title,
                item.source_name,
                cat,
            )

        self.console.print(table)

    def _render_source_summary(self, by_source: dict[str, list[NewsItem]]) -> None:
        table = Table(
            title=f"📊 {t('term.source_summary')}",
            show_header=True,
            header_style="bold blue",
            border_style="dim",
        )
        table.add_column(t("term.source_col_source"), style="cyan", min_width=16)
        table.add_column(t("term.source_col_items"), style="white", justify="right", width=6)

        for source_name, source_items in sorted(by_source.items(), key=lambda x: -len(x[1])):
            table.add_row(source_name, str(len(source_items)))

        self.console.print(table)
        self.console.print()
