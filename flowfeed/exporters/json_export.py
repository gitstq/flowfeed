"""JSON export format."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO

from flowfeed.sources.base import NewsItem


class JSONExporter:
    """Export news items to JSON format."""

    def export(
        self,
        items: list[NewsItem],
        output: str | Path | TextIO | None = None,
        pretty: bool = True,
    ) -> str:
        """Export items as JSON string, optionally write to file."""
        data = {
            "total": len(items),
            "items": [item.to_dict() for item in items],
        }

        indent = 2 if pretty else None
        result = json.dumps(data, ensure_ascii=False, indent=indent, default=str)

        if output is not None:
            if isinstance(output, (str, Path)):
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(result, encoding="utf-8")
            else:
                output.write(result)

        return result
