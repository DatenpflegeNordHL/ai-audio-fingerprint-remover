"""Markdown report output."""

from __future__ import annotations

from pathlib import Path
from typing import Any


SAFETY_NOTE = (
    "This report is an audio quality and release-readiness preflight. "
    "It does not evaluate or alter watermarks, fingerprints, provenance markers, "
    "origin markers, detector signals, or source-attribution systems."
)

HUMANIZE_SAFETY_NOTE = (
    "This report describes conservative audible-quality processing. "
    "It does not evaluate or alter watermarks, fingerprints, provenance markers, "
    "origin markers, detector signals, C2PA markers, or attribution systems."
)

WORKFLOW_SAFETY_NOTE = (
    "These workflow reports are technical audio-quality and metadata preflights. "
    "They do not evaluate or alter watermarks, fingerprints, detector signals, "
    "provenance markers, origin markers, C2PA markers, or attribution systems."
)


def write_markdown_report(report: dict, path: Path) -> None:
    """Write a compact Markdown report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(report), encoding="utf-8")


def _render_markdown(report: dict) -> str:
    if report.get("action") == "batch":
        return _render_batch_markdown(report)
    if report.get("action") == "doctor":
        return _render_doctor_markdown(report)
    if report.get("action") == "humanize":
        return _render_humanize_markdown(report)
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
    if action == "humanize":
        return "Conservative Humanize Report"
    if action == "doctor":
        return "Doctor Preflight"
    if action == "batch":
        return "Batch Workflow Report"
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


def _render_humanize_markdown(report: dict) -> str:
    safety = report.get("safety", {})
    comparison = report.get("comparison", {})
    lines = [
        "# Conservative Humanize Report",
        "",
        f"- Action: `{report.get('action', 'humanize')}`",
        f"- Preset: `{report.get('preset', '')}`",
        f"- Target: `{report.get('target', '')}`",
        f"- Input: `{report.get('input', '')}`",
        f"- Output: `{report.get('output', '')}`",
        f"- Passed: `{report.get('passed')}`",
        f"- Reverted: `{report.get('reverted')}`",
        f"- Compare Score: `{comparison.get('score')}`",
    ]

    _add_processing_steps_table(lines, report.get("processing_steps", []))
    _add_before_after_metrics_table(lines, report.get("before_analysis", {}), report.get("after_analysis", {}))
    _add_table_section(lines, "Metric Deltas", comparison.get("metric_deltas", {}))
    _add_list_section(lines, "Safety Blocking Issues", safety.get("blocking_issues", []))
    _add_list_section(lines, "Warnings", safety.get("warnings", []))
    _add_list_section(lines, "Recommendations", safety.get("recommendations", []))

    lines.extend(["", "## Safety Note", "", HUMANIZE_SAFETY_NOTE, ""])
    return "\n".join(lines)


def _add_processing_steps_table(lines: list[str], steps: list[dict[str, Any]]) -> None:
    lines.extend(["", "## Processing Steps", "", "| Step | Applied | Detail |", "| --- | --- | --- |"])
    if not steps:
        lines.append("| None |  |  |")
        return
    for step in steps:
        name = step.get("name", "")
        applied = step.get("applied", False)
        details = ", ".join(f"{key}={_format_value(value)}" for key, value in step.items() if key not in {"name", "applied"})
        lines.append(f"| `{name}` | `{applied}` | `{details}` |")


def _add_before_after_metrics_table(lines: list[str], before: dict, after: dict) -> None:
    lines.extend(["", "## Before / After Key Metrics", "", "| Metric | Before | After |", "| --- | --- | --- |"])
    for key in _key_metric_names():
        if key in before or key in after:
            lines.append(f"| `{key}` | `{_format_value(before.get(key))}` | `{_format_value(after.get(key))}` |")


def _render_doctor_markdown(report: dict) -> str:
    analysis = report.get("analysis", {})
    release = report.get("release_check", {})
    metadata = report.get("metadata", {}).get("metadata", {})
    provenance = report.get("provenance", {})
    lines = [
        "# Doctor Preflight",
        "",
        f"- Target: `{report.get('target', '')}`",
        f"- Input: `{report.get('input', '')}`",
        f"- Passed: `{report.get('passed')}`",
        f"- Score: `{report.get('score')}`",
    ]

    lines.extend(["", "## Key Audio Metrics", "", "| Metric | Value |", "| --- | --- |"])
    for key in _key_metric_names():
        if key in analysis:
            lines.append(f"| `{key}` | `{_format_value(analysis[key])}` |")

    _add_list_section(lines, "Release Blocking Issues", release.get("blocking_issues", []))
    _add_list_section(lines, "Warnings", report.get("warnings", []))
    _add_list_section(lines, "Recommendations", report.get("recommendations", []))

    lines.extend(
        [
            "",
            "## Metadata / Provenance Summary",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| `detected_metadata_keys` | `{len(metadata.get('detected_metadata_keys', []))}` |",
            f"| `ordinary_metadata_keys` | `{len(metadata.get('ordinary_metadata_keys', []))}` |",
            f"| `possible_provenance_keys` | `{len(provenance.get('possible_provenance_keys', []))}` |",
            f"| `metadata_read_error` | `{_format_value(metadata.get('metadata_read_error'))}` |",
        ]
    )

    lines.extend(["", "## Safety Note", "", WORKFLOW_SAFETY_NOTE, ""])
    return "\n".join(lines)


def _render_batch_markdown(report: dict) -> str:
    lines = [
        "# Batch Workflow Report",
        "",
        f"- Mode: `{report.get('mode', '')}`",
        f"- Target: `{report.get('target', '')}`",
        f"- Preset: `{report.get('preset', '')}`",
        f"- Input Directory: `{report.get('input_dir', '')}`",
        f"- Output Directory: `{report.get('output_dir')}`",
        f"- Total Files: `{report.get('total_files')}`",
        f"- Processed Files: `{report.get('processed_files')}`",
        f"- Failed Files: `{report.get('failed_files')}`",
        f"- Passed Files: `{report.get('passed_files')}`",
    ]

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| Input | Output | Report | Passed | Error | Score |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for result in report.get("results", []):
        lines.append(
            "| "
            f"`{result.get('input')}` | "
            f"`{result.get('output')}` | "
            f"`{result.get('report')}` | "
            f"`{result.get('passed')}` | "
            f"`{_format_value(result.get('error'))}` | "
            f"`{_format_value(result.get('score'))}` |"
        )
    if not report.get("results"):
        lines.append("| None |  |  |  |  |  |")

    _add_list_section(lines, "Warnings", report.get("warnings", []))
    lines.extend(["", "## Safety Note", "", WORKFLOW_SAFETY_NOTE, ""])
    return "\n".join(lines)
