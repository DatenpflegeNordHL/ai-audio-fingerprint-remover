"""Markdown report output."""

from __future__ import annotations

from pathlib import Path
from typing import Any


SAFETY_NOTE = (
    "This report is an audio quality and release-readiness preflight. "
    "It does not evaluate or alter watermarks, fingerprints, provenance markers, "
    "origin markers, detector signals, or source-attribution systems."
)


def write_markdown_report(report: dict, path: Path) -> None:
    """Write a compact Markdown report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(report), encoding="utf-8")


def _render_markdown(report: dict) -> str:
    if report.get("action") == "compare":
        return _render_compare_markdown(report)

    title = _title_for_report(report)
    lines = [
        f"# {title}",
        "",
        f"- Action: `{report.get('action', 'unknown')}`",
    ]
    if "target" in report:
        lines.append(f"- Target: `{report['target']}`")
    if "score" in report:
        lines.append(f"- Score: `{report['score']}`")
    if "passed" in report:
        lines.append(f"- Passed: `{report['passed']}`")

    metrics_source = report.get("analysis", report)
    lines.extend(["", "## Key Metrics", "", "| Metric | Value |", "| --- | --- |"])
    for key in _key_metric_names():
        if key in metrics_source:
            lines.append(f"| `{key}` | `{_format_value(metrics_source[key])}` |")

    _add_list_section(lines, "Warnings", report.get("warnings", metrics_source.get("warnings", [])))
    _add_list_section(lines, "Blocking Issues", report.get("blocking_issues", []))
    _add_list_section(lines, "Recommendations", report.get("recommendations", []))

    lines.extend(["", "## Safety Note", "", SAFETY_NOTE, ""])
    return "\n".join(lines)


def _title_for_report(report: dict) -> str:
    action = report.get("action")
    if action == "compare":
        return "Audio Compare Preflight"
    if action == "release_check":
        return "Release-Readiness Preflight"
    if action == "analyze":
        return "Audio Quality Analysis"
    return "audio-quality-humanizer Report"


def _key_metric_names() -> list[str]:
    return [
        "duration_seconds",
        "samplerate",
        "channels",
        "peak_dbfs",
        "rms_dbfs",
        "loudness_lufs_approx",
        "crest_factor_db",
        "clipping_sample_count",
        "clipping_ratio",
        "dynamic_range_estimate_db",
        "spectral_centroid_hz",
        "spectral_rolloff_95_hz",
        "low_mid_mud_energy_ratio_180_450_hz",
        "harshness_energy_ratio_6000_12000_hz",
        "stereo_correlation",
        "side_energy_ratio",
    ]


def _add_list_section(lines: list[str], title: str, values: list[str]) -> None:
    lines.extend(["", f"## {title}", ""])
    if not values:
        lines.append("None.")
        return
    for value in values:
        lines.append(f"- {value}")


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _render_compare_markdown(report: dict) -> str:
    reference = report.get("reference", {})
    candidate = report.get("candidate", {})
    lines = [
        "# Audio Compare Preflight",
        "",
        f"- Action: `{report.get('action', 'compare')}`",
        f"- Reference: `{reference.get('path', '')}`",
        f"- Candidate: `{candidate.get('path', '')}`",
        f"- Target: `{report.get('target', '')}`",
        f"- Passed: `{report.get('passed')}`",
        f"- Score: `{report.get('score')}`",
    ]

    _add_table_section(lines, "Compatibility", report.get("compatibility", {}))
    _add_table_section(lines, "Key Metric Deltas", report.get("metric_deltas", {}))
    _add_table_section(lines, "Waveform Similarity", report.get("waveform_similarity", {}))
    _add_regression_section(lines, report.get("regressions", []))
    _add_list_section(lines, "Warnings", report.get("warnings", []))
    _add_list_section(lines, "Recommendations", report.get("recommendations", []))

    lines.extend(["", "## Safety Note", "", SAFETY_NOTE, ""])
    return "\n".join(lines)


def _add_table_section(lines: list[str], title: str, values: dict[str, Any]) -> None:
    lines.extend(["", f"## {title}", "", "| Field | Value |", "| --- | --- |"])
    if not values:
        lines.append("| None |  |")
        return
    for key, value in values.items():
        lines.append(f"| `{key}` | `{_format_value(value)}` |")


def _add_regression_section(lines: list[str], regressions: list[dict[str, str]]) -> None:
    lines.extend(["", "## Regressions", ""])
    if not regressions:
        lines.append("None.")
        return
    for item in regressions:
        severity = item.get("severity", "unknown")
        message = item.get("message", "")
        lines.append(f"- `{severity}`: {message}")
