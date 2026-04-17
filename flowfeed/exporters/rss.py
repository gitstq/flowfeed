"""RSS export format."""

from __future__ import annotations

import html as html_mod
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path
from typing import TextIO

from flowfeed.i18n import t
from flowfeed.sources.base import NewsItem

RSS_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{rss_title}</title>
    <link>https://github.com/gitstq/flowfeed</link>
    <description>{rss_description}</description>
    <language>{rss_language}</language>
    <lastBuildDate>{build_date}</lastBuildDate>
    <generator>FlowFeed v1.1.0</generator>
    {items}
  </channel>
</rss>
"""

ITEM_TEMPLATE = """\
    <item>
      <title>{title}</title>
      <link>{url}</link>
      <description>{description}</description>
      <category>{source_name}</category>
      <pubDate>{pub_date}</pubDate>
    </item>
"""


class RSSExporter:
    """Export news items to RSS 2.0 XML format."""

    def export(
        self,
        items: list[NewsItem],
        output: str | Path | TextIO | None = None,
        title: str = "FlowFeed",
    ) -> str:
        """Export items as RSS XML string, optionally write to file."""
        build_date = formatdate(usegmt=True)
        item_xmls: list[str] = []

        for item in items[:100]:  # RSS feeds typically limit to ~100 items
            escaped_title = html_mod.escape(item.title)
            escaped_url = html_mod.escape(item.url)
            escaped_desc = html_mod.escape(item.summary or item.title)
            escaped_source = html_mod.escape(item.source_name)
            pub_date = formatdate(
                timeval=item.fetched_at.timestamp(),
                localtime=False,
                usegmt=True,
            )
            item_xmls.append(ITEM_TEMPLATE.format(
                title=escaped_title,
                url=escaped_url,
                description=escaped_desc,
                source_name=escaped_source,
                pub_date=pub_date,
            ))

        result = RSS_TEMPLATE.format(
            rss_title=t("rss.title"),
            rss_description=t("rss.description"),
            rss_language=t("rss.language"),
            build_date=build_date,
            items="\n".join(item_xmls),
        )

        if output is not None:
            if isinstance(output, (str, Path)):
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(result, encoding="utf-8")
            else:
                output.write(result)

        return result
