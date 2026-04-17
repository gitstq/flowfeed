"""HTML Report exporter — generates a beautiful web dashboard."""

from __future__ import annotations

import html as html_mod
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

from jinja2 import Template

from flowfeed.i18n import t
from flowfeed.sources.base import NewsItem

HTML_TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="{{ html_lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        :root {
            --bg: #0f172a;
            --surface: #1e293b;
            --border: #334155;
            --text: #e2e8f0;
            --text-dim: #94a3b8;
            --accent: #38bdf8;
            --accent2: #818cf8;
            --hot: #f97316;
            --green: #4ade80;
            --red: #f87171;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header {
            text-align: center;
            padding: 2rem 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 2rem;
        }
        .header h1 {
            font-size: 2rem;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .header .meta { color: var(--text-dim); margin-top: 0.5rem; }
        .stats {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            margin: 1.5rem 0;
        }
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            text-align: center;
            min-width: 120px;
        }
        .stat-card .value {
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent);
        }
        .stat-card .label { color: var(--text-dim); font-size: 0.85rem; }
        .source-section {
            margin-bottom: 2rem;
        }
        .source-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }
        .source-header h2 { font-size: 1.2rem; }
        .source-header .badge {
            background: var(--accent);
            color: var(--bg);
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: bold;
        }
        .item {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 0.25rem;
            transition: background 0.2s;
        }
        .item:hover { background: var(--surface); }
        .item .rank {
            font-weight: bold;
            color: var(--accent);
            min-width: 2rem;
            text-align: center;
            font-size: 0.9rem;
        }
        .item .rank.top3 { color: var(--hot); }
        .item .content { flex: 1; min-width: 0; }
        .item .title {
            color: var(--text);
            text-decoration: none;
            font-weight: 500;
        }
        .item .title:hover { color: var(--accent); }
        .item .title:visited { color: var(--accent2); }
        .item .meta-info {
            color: var(--text-dim);
            font-size: 0.8rem;
            margin-top: 0.25rem;
        }
        .item .score {
            background: var(--hot);
            color: white;
            padding: 0.1rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            white-space: nowrap;
        }
        .footer {
            text-align: center;
            padding: 2rem 0;
            border-top: 1px solid var(--border);
            margin-top: 2rem;
            color: var(--text-dim);
            font-size: 0.85rem;
        }
        .footer a { color: var(--accent); text-decoration: none; }
        @media (max-width: 640px) {
            .container { padding: 1rem; }
            .header h1 { font-size: 1.5rem; }
            .stats { gap: 0.5rem; }
            .stat-card { min-width: 80px; padding: 0.75rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📡 FlowFeed</h1>
            <p class="meta">{{ meta_text }}</p>
        </div>
        <div class="stats">
            <div class="stat-card">
                <div class="value">{{ total_items }}</div>
                <div class="label">{{ stat_total }}</div>
            </div>
            <div class="stat-card">
                <div class="value">{{ total_sources }}</div>
                <div class="label">{{ stat_sources }}</div>
            </div>
            <div class="stat-card">
                <div class="value">{{ top_score }}</div>
                <div class="label">{{ stat_top_score }}</div>
            </div>
        </div>
        {% for source_name, source_items in grouped.items() %}
        <div class="source-section">
            <div class="source-header">
                <h2>📡 {{ source_name }}</h2>
                <span class="badge">{{ source_items | length }}</span>
            </div>
            {% for item in source_items %}
            <div class="item">
                <span class="rank {{ 'top3' if item.rank <= 3 }}">{{ item.rank }}</span>
                <div class="content">
                    <a class="title" href="{{ item.url }}" target="_blank" rel="noopener">{{ item.title }}</a>
                    {% if item.summary %}
                    <div class="meta-info">{{ item.summary[:100] }}</div>
                    {% endif %}
                </div>
                {% if item.hot_score > 0 %}
                <span class="score">🔥 {{ "%.0f" | format(item.hot_score) }}</span>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endfor %}
        <div class="footer">
            <p>{{ footer_text }}</p>
        </div>
    </div>
</body>
</html>
""")


class HTMLReportExporter:
    """Export news items to a self-contained HTML dashboard."""

    def export(
        self,
        items: list[NewsItem],
        output: str | Path | TextIO | None = None,
        title: str = "FlowFeed Dashboard",
    ) -> str:
        """Generate HTML dashboard, optionally write to file."""
        # Group by source
        grouped: dict[str, list[dict]] = {}
        for item in items:
            grouped.setdefault(item.source_name, []).append(item.to_dict())

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        top_score = f"{items[0].hot_score:.0f}" if items else "0"

        html = HTML_TEMPLATE.render(
            title=title,
            html_lang=t("html.lang"),
            meta_text=t("html.meta", time=now, items=len(items), sources=len(grouped)),
            stat_total=t("html.stat_total"),
            stat_sources=t("html.stat_sources"),
            stat_top_score=t("html.stat_top_score"),
            total_items=len(items),
            total_sources=len(grouped),
            top_score=top_score,
            grouped=grouped,
            footer_text=t("html.footer"),
        )

        if output is not None:
            if isinstance(output, (str, Path)):
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(html, encoding="utf-8")
            else:
                output.write(html)

        return html
