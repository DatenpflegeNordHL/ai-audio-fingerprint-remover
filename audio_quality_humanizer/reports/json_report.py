"""JSON report output."""

from __future__ import annotations

import json
from pathlib import Path


def write_json_report(report: dict, path: Path) -> None:
    """Write a stable, pretty JSON report as UTF-8."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
