"""Lightweight operational performance metadata."""

from __future__ import annotations

import platform
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any


class _OperationMeasurement:
    def __init__(self, label: str):
        self.metrics = _base_metrics(label)
        self._start: float | None = None

    def __enter__(self) -> dict[str, Any]:
        self._start = time.perf_counter()
        return self.metrics

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._start is not None:
            self.metrics["elapsed_seconds"] = round(time.perf_counter() - self._start, 6)


def measure_operation(label: str, callable_or_context: Callable[[], Any] | None = None) -> Any:
    """Measure elapsed seconds for a callable or return a context manager."""

    if callable_or_context is None:
        return _OperationMeasurement(label)

    with _OperationMeasurement(label) as metrics:
        result = callable_or_context()
    return {"result": result, "performance": metrics}


def collect_file_stats(path: Path) -> dict[str, Any]:
    """Return JSON-safe file metadata for report context."""

    path = Path(path)
    exists = path.exists()
    is_file = path.is_file() if exists else False
    return {
        "path": str(path),
        "exists": bool(exists),
        "is_file": bool(is_file),
        "size_bytes": int(path.stat().st_size) if is_file else 0,
    }


def estimate_report_size(path: Path) -> dict[str, Any]:
    """Return report size metadata without reading report contents."""

    stats = collect_file_stats(path)
    return {
        "path": stats["path"],
        "exists": stats["exists"],
        "report_size_bytes": stats["size_bytes"],
    }


def add_file_sizes(
    metrics: dict[str, Any],
    *,
    input_path: Path | None = None,
    output_path: Path | None = None,
    report_path: Path | None = None,
) -> dict[str, Any]:
    """Attach optional input, output, and report sizes to a metrics dictionary."""

    if input_path is not None:
        metrics["input_size_bytes"] = collect_file_stats(input_path)["size_bytes"]
    if output_path is not None:
        metrics["output_size_bytes"] = collect_file_stats(output_path)["size_bytes"]
    if report_path is not None:
        metrics["report_size_bytes"] = estimate_report_size(report_path)["report_size_bytes"]
    return metrics


def _base_metrics(label: str) -> dict[str, Any]:
    return {
        "operation": str(label),
        "elapsed_seconds": 0.0,
        "input_size_bytes": 0,
        "output_size_bytes": 0,
        "report_size_bytes": 0,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
    }
