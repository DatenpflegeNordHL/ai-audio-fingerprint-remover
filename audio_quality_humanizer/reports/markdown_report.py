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

PRESET_EVAL_SAFETY_NOTE = (
    "This preset evaluation only compares conservative audio-quality processing outcomes. "
    "It does not evaluate or alter watermarks, fingerprints, detector signals, provenance "
    "markers, origin markers, C2PA markers, or attribution systems."
)

VALIDATION_SAFETY_NOTE = (
    "This validation workflow only evaluates local user-supplied audio-quality and release-readiness outcomes. "
    "It does not evaluate or alter watermarks, fingerprints, detector signals, provenance markers, "
    "origin markers, C2PA markers, or attribution systems."
)

VALIDATION_STATUS_SAFETY_NOTE = (
    "This status command only inspects local file paths and validation report presence. "
    "It does not read, process, evaluate, or alter audio, watermarks, fingerprints, "
    "detector signals, provenance markers, origin markers, C2PA markers, or attribution systems."
)


def write_markdown_report(report: dict, path: Path) -> None:
    """Write a compact Markdown report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(report), encoding="utf-8")


def _render_markdown(report: dict) -> str:
    if report.get("action") == "validation_status":
        return _render_validation_status_markdown(report)
    if report.get("action") == "validate_samples":
        return _render_validate_samples_markdown(report)
    if report.get("action") == "preset_eval":
        return _render_preset_eval_markdown(report)
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

    _add_guardrails_section(lines, report)
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
    if action == "preset_eval":
        return "Preset Evaluation Report"
    if action == "validate_samples":
        return "Real-World Sample Validation Report"
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
    status = _humanize_status(report)
    main_issue = _first_item(safety.get("blocking_issues", []))
    lines = [
        "# Conservative Humanize Report",
        "",
        "## Summary",
        "",
        f"- Status: `{status}`",
        f"- Action: `{report.get('action', 'humanize')}`",
        f"- Preset: `{report.get('preset', '')}`",
        f"- Target: `{report.get('target', '')}`",
        f"- Input: `{report.get('input', '')}`",
        f"- Output: `{report.get('output', '')}`",
        f"- Passed: `{report.get('passed')}`",
        f"- Reverted: `{report.get('reverted')}`",
        f"- Safety Result: `{safety.get('passed')}`",
        f"- Compare Score: `{comparison.get('score')}`",
        f"- Main Safety Issue: `{_format_value(main_issue)}`",
        "- Original input was not modified.",
    ]

    _add_processing_steps_table(lines, report.get("processing_steps", []))
    _add_guardrails_section(lines, report)
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
    status = _doctor_status(report)
    main_issue = _first_item(report.get("blocking_issues", [])) or _first_item(report.get("warnings", []))
    suggested_action = _doctor_suggested_action(report)
    lines = [
        "# Doctor Preflight",
        "",
        "## Summary",
        "",
        f"- Status: `{status}`",
        f"- Target: `{report.get('target', '')}`",
        f"- Input: `{report.get('input', '')}`",
        f"- Passed: `{report.get('passed')}`",
        f"- Score: `{report.get('score')}`",
        f"- Main Issue: `{_format_value(main_issue)}`",
        f"- Suggested Next Action: `{suggested_action}`",
    ]

    top_recommendations = report.get("recommendations", [])[:3]
    _add_list_section(lines, "Top Recommendations", top_recommendations)

    lines.extend(["", "## Key Audio Metrics", "", "| Metric | Value |", "| --- | --- |"])
    for key in _key_metric_names():
        if key in analysis:
            lines.append(f"| `{key}` | `{_format_value(analysis[key])}` |")

    _add_guardrails_section(lines, report)
    _add_performance_section(lines, report)
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


def _render_preset_eval_markdown(report: dict) -> str:
    doctor = report.get("doctor", {})
    lines = [
        "# Preset Evaluation Report",
        "",
        f"- Input: `{report.get('input', '')}`",
        f"- Target: `{report.get('target', '')}`",
        f"- Output Directory: `{report.get('output_dir', '')}`",
        f"- Recommended Preset: `{report.get('recommended_preset')}`",
        f"- Recommendation Reason: `{report.get('recommendation_reason', '')}`",
        f"- Doctor Score: `{doctor.get('score')}`",
        f"- Doctor Passed: `{doctor.get('passed')}`",
    ]

    lines.extend(
        [
            "",
            "## Preset Results",
            "",
            "| Preset | Humanize Passed | Reverted | Compare Passed | Compare Score | Release Passed | Release Score | Warning Count | Output |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for result in report.get("results", []):
        lines.append(
            "| "
            f"`{result.get('preset')}` | "
            f"`{result.get('humanize_passed')}` | "
            f"`{result.get('humanize_reverted')}` | "
            f"`{result.get('compare_passed')}` | "
            f"`{_format_value(result.get('compare_score'))}` | "
            f"`{result.get('release_passed')}` | "
            f"`{_format_value(result.get('release_score'))}` | "
            f"`{len(result.get('warnings', []))}` | "
            f"`{result.get('output')}` |"
        )
    if not report.get("results"):
        lines.append("| None |  |  |  |  |  |  |  |  |")

    blocking_issues = []
    for result in report.get("results", []):
        for issue in result.get("blocking_issues", []):
            blocking_issues.append(f"{result.get('preset')}: {issue}")
        if result.get("error"):
            blocking_issues.append(f"{result.get('preset')}: {result.get('error')}")
    _add_list_section(lines, "Blocking Issues", blocking_issues)
    warnings = list(report.get("warnings", []))
    for result in report.get("results", []):
        for warning in result.get("warnings", []):
            warnings.append(f"{result.get('preset')}: {warning}")
    _add_list_section(lines, "Warnings", warnings)
    lines.extend(["", "## Safety Note", "", PRESET_EVAL_SAFETY_NOTE, ""])
    return "\n".join(lines)


def _render_validate_samples_markdown(report: dict) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Real-World Sample Validation Report",
        "",
        f"- Project: `{report.get('project')}`",
        f"- Manifest: `{report.get('manifest', '')}`",
        f"- Output Directory: `{report.get('output_dir', '')}`",
        f"- Total Samples: `{report.get('total_samples')}`",
        f"- Processed Samples: `{report.get('processed_samples')}`",
        f"- Failed Samples: `{report.get('failed_samples')}`",
        f"- Passed Samples: `{report.get('passed_samples')}`",
        f"- Average Doctor Score: `{_format_value(summary.get('average_doctor_score'))}`",
    ]

    _add_table_section(lines, "Recommended Preset Counts", summary.get("recommended_preset_counts", {}))
    _add_performance_section(lines, report)

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| ID | Target | Doctor Score | Doctor Passed | Recommended Preset | Original Unchanged | Error |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for result in report.get("results", []):
        lines.append(
            "| "
            f"`{result.get('id')}` | "
            f"`{result.get('target')}` | "
            f"`{_format_value(result.get('doctor_score'))}` | "
            f"`{result.get('doctor_passed')}` | "
            f"`{result.get('recommended_preset')}` | "
            f"`{result.get('original_unchanged')}` | "
            f"`{_format_value(result.get('error'))}` |"
        )
    if not report.get("results"):
        lines.append("| None |  |  |  |  |  |  |")

    _add_list_section(lines, "Warnings", report.get("warnings", []))
    _add_list_section(lines, "Notes", report.get("notes", []))
    lines.extend(["", "## Safety Note", "", VALIDATION_SAFETY_NOTE, ""])
    return "\n".join(lines)


def _render_validation_status_markdown(report: dict) -> str:
    lines = [
        "# Validation Status Report",
        "",
        "## Summary",
        "",
        f"- Current Directory: `{report.get('cwd', '')}`",
        f"- Inspected Root: `{report.get('root', '')}`",
        f"- Looks Like Project Root: `{report.get('looks_like_project_root')}`",
        f"- Project Root Hint: `{_format_value(report.get('project_root_hint'))}`",
        f"- Virtualenv Python Exists: `{report.get('venv_python_exists')}`",
        f"- Virtualenv CLI Exists: `{report.get('venv_cli_exists')}`",
        f"- Validation Manifest Exists: `{report.get('validation_manifest_exists')}`",
        f"- Validation JSON Exists: `{report.get('validation_json_exists')}`",
        f"- Validation Markdown Exists: `{report.get('validation_markdown_exists')}`",
        f"- Validation Samples Directory Exists: `{report.get('validation_samples_dir_exists')}`",
        f"- Validation Outputs Directory Exists: `{report.get('validation_outputs_dir_exists')}`",
    ]

    lines.extend(
        [
            "",
            "## Found Reports",
            "",
            "| Path |",
            "| --- |",
        ]
    )
    for path in report.get("found_reports", []):
        lines.append(f"| `{path}` |")
    if not report.get("found_reports"):
        lines.append("| None |")

    _add_list_section(lines, "Suggested Commands", report.get("suggested_commands", []))
    _add_list_section(lines, "Warnings", report.get("warnings", []))
    _add_list_section(lines, "Notes", report.get("notes", []))
    lines.extend(["", "## Safety Note", "", VALIDATION_STATUS_SAFETY_NOTE, ""])
    return "\n".join(lines)


def _doctor_status(report: dict) -> str:
    if report.get("blocking_issues"):
        return "BLOCKED"
    if report.get("warnings"):
        return "WARNING"
    return "PASS"


def _humanize_status(report: dict) -> str:
    if report.get("reverted"):
        return "REVERTED"
    if not report.get("passed"):
        return "BLOCKED"
    return "PASS"


def _doctor_suggested_action(report: dict) -> str:
    release = report.get("release_check", {})
    analysis_warnings = " ".join(report.get("analysis", {}).get("warnings", [])).casefold()
    metadata = report.get("metadata", {}).get("metadata", {})
    provenance = report.get("provenance", {})
    if release.get("blocking_issues"):
        return "Fix blocking release issues before processing."
    if metadata.get("ordinary_metadata_keys"):
        return "Run clean-metadata on a copy if metadata cleanup is desired."
    if provenance.get("possible_provenance_keys"):
        return "Review possible provenance metadata manually."
    if "low-end stereo" in analysis_warnings:
        return "Try preset-eval with club or afro-club for club target."
    if "harshness" in analysis_warnings or "mud" in analysis_warnings:
        return "Try preset-eval with balanced or afro-club depending on target."
    if release.get("passed") and len(report.get("warnings", [])) <= 2:
        return "No processing needed unless you hear audible issues."
    return "Review warnings and run preset-eval if audible processing is needed."


def _first_item(values: list[Any]) -> Any:
    return values[0] if values else None


def _add_guardrails_section(lines: list[str], report: dict) -> None:
    guardrails = _guardrails_for_report(report)
    if not guardrails:
        return

    nan_count = int(guardrails.get("nan_count_before", 0) or 0) + int(guardrails.get("nan_count_after", 0) or 0)
    inf_count = int(guardrails.get("inf_count_before", 0) or 0) + int(guardrails.get("inf_count_after", 0) or 0)
    lines.extend(
        [
            "",
            "## Signal Guardrails",
            "",
            f"- Input valid: `{guardrails.get('input_valid')}`",
            f"- Output valid: `{_format_value(guardrails.get('output_valid'))}`",
            f"- NaN values detected: `{nan_count}`",
            f"- Infinite values detected: `{inf_count}`",
            f"- Shape changed: `{guardrails.get('shape_changed')}`",
            f"- Length changed: `{guardrails.get('length_changed')}`",
            f"- Actions: `{_format_value(_join_values(guardrails.get('actions', [])))}`",
            f"- Warnings: `{_format_value(_join_values(guardrails.get('warnings', [])))}`",
        ]
    )


def _add_performance_section(lines: list[str], report: dict) -> None:
    performance = report.get("performance", {})
    if not performance:
        return

    lines.extend(
        [
            "",
            "## Performance Metadata",
            "",
            "| Field | Value |",
            "| --- | --- |",
        ]
    )
    for key in (
        "operation",
        "elapsed_seconds",
        "input_size_bytes",
        "output_size_bytes",
        "report_size_bytes",
        "python_version",
        "platform",
    ):
        if key in performance:
            lines.append(f"| `{key}` | `{_format_value(performance[key])}` |")


def _guardrails_for_report(report: dict) -> dict:
    if isinstance(report.get("guardrails"), dict) and report["guardrails"]:
        return report["guardrails"]
    analysis = report.get("analysis", {})
    if isinstance(analysis, dict) and isinstance(analysis.get("guardrails"), dict):
        return analysis["guardrails"]
    return {}


def _join_values(values: list[Any]) -> str:
    if not values:
        return "None."
    return "; ".join(str(value) for value in values)
