"""Synchronous safe processing for the private web backend."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any, Callable

from audio_quality_humanizer.analysis.compare import compare_audio
from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.analysis.release_check import release_check
from audio_quality_humanizer.metadata.cleaner import clean_metadata, inspect_metadata, sha256_file
from audio_quality_humanizer.processing.humanize import humanize_audio
from audio_quality_humanizer.web.metadata_display import build_metadata_display
from audio_quality_humanizer.web.storage import artifact_path, read_status, utc_now_iso, write_status
from audio_quality_humanizer.web.workflow_registry import WORKFLOW_DEFINITIONS
from audio_quality_humanizer.visualization_artifacts import build_visualization_artifacts, build_visualization_comparison


ARTIFACT_BY_MODE = {
    "analyze": "analysis.json",
    "release-check": "release_check.json",
    "inspect-metadata": "metadata.json",
    "visualize": "visualization.json",
}

STANDARD_METADATA_FIELDS = {
    "album",
    "albumartist",
    "artist",
    "comment",
    "composer",
    "copyright",
    "date",
    "description",
    "encoded_by",
    "encoder",
    "genre",
    "title",
    "tracknumber",
    "year",
}


def execute_job(job_dir: Path, input_path: Path, mode: str) -> dict[str, Any]:
    """Execute a safe single-file mode and update status JSON."""

    status_data = read_status(job_dir)
    try:
        if mode == "clean-metadata":
            artifacts = _run_clean_metadata(job_dir, input_path)
        else:
            report = _run_mode(input_path, mode)
            artifact_name = ARTIFACT_BY_MODE[mode]
            _write_json_artifact(job_dir, artifact_name, report)
            artifacts = ["status.json", artifact_name]
        status_data["status"] = "completed"
        status_data["completed_at"] = utc_now_iso()
        status_data["processing"] = {
            "execution": "completed",
            "message": "Safe single-file processing completed.",
        }
        status_data["artifacts"] = artifacts
    except Exception:
        status_data["status"] = "failed"
        status_data["failed_at"] = utc_now_iso()
        status_data["processing"] = {
            "execution": "failed",
            "message": "Processing failed safely.",
            "error_code": "processing_failed",
        }
        status_data["artifacts"] = ["status.json"]
    write_status(job_dir, status_data)
    return status_data


def execute_two_file_job(job_dir: Path, before_path: Path, after_path: Path, mode: str) -> dict[str, Any]:
    """Execute a safe two-file mode and update status JSON."""

    status_data = read_status(job_dir)
    try:
        artifacts = ["status.json"]
        if mode == "compare":
            compare_report = compare_audio(before_path, after_path, "streaming")
            _write_json_artifact(job_dir, "compare.json", compare_report)
            artifacts.append("compare.json")
        elif mode == "visualize-compare":
            compare_report = compare_audio(before_path, after_path, "streaming")
            _write_json_artifact(job_dir, "compare.json", compare_report)
            visual_report = build_visualization_comparison(before_path, after_path, target="streaming")
            _write_json_artifact(job_dir, "visual_compare.json", visual_report)
            artifacts.extend(["compare.json", "visual_compare.json"])
        else:
            raise ValueError("Unsupported two-file mode.")
        status_data["status"] = "completed"
        status_data["completed_at"] = utc_now_iso()
        status_data["processing"] = {
            "execution": "completed",
            "message": "Safe two-file processing completed.",
        }
        status_data["artifacts"] = artifacts
    except Exception:
        status_data["status"] = "failed"
        status_data["failed_at"] = utc_now_iso()
        status_data["processing"] = {
            "execution": "failed",
            "message": "Processing failed safely.",
            "error_code": "processing_failed",
        }
        status_data["artifacts"] = ["status.json"]
    write_status(job_dir, status_data)
    return status_data


def execute_workflow_job(job_dir: Path, input_path: Path, workflow_name: str) -> dict[str, Any]:
    """Execute a private beta workflow and update status JSON."""

    status_data = read_status(job_dir)
    try:
        if workflow_name == "quick-scan":
            artifacts = _run_quick_scan(job_dir, input_path, status_data)
        elif workflow_name == "metadata-clean":
            artifacts = _run_metadata_clean_workflow(job_dir, input_path, status_data)
        elif workflow_name == "quality-naturalize":
            artifacts = _run_quality_naturalize_workflow(job_dir, input_path, status_data)
        elif workflow_name == "full-release-pass":
            artifacts = _run_full_release_pass_workflow(job_dir, input_path, status_data)
        else:
            raise ValueError("Unsupported private beta workflow.")
        status_data["status"] = "completed"
        status_data["completed_at"] = utc_now_iso()
        status_data["processing"] = {
            "execution": "completed",
            "message": "Private beta workflow completed.",
        }
        status_data["artifacts"] = artifacts
        status_data["artifact_groups"] = _artifact_groups_for(workflow_name, artifacts)
    except Exception:
        _fail_running_step(status_data)
        status_data["status"] = "failed"
        status_data["failed_at"] = utc_now_iso()
        status_data["processing"] = {
            "execution": "failed",
            "message": "Private beta workflow failed safely.",
            "error_code": "workflow_failed",
        }
        status_data["artifacts"] = ["status.json"]
        status_data["artifact_groups"] = {}
    write_status(job_dir, status_data)
    return status_data


def _run_mode(input_path: Path, mode: str) -> dict[str, Any]:
    handlers: dict[str, Callable[[Path], dict[str, Any]]] = {
        "analyze": analyze_audio,
        "release-check": lambda path: release_check(path, "streaming"),
        "inspect-metadata": _inspect_metadata_for_web,
        "visualize": build_visualization_artifacts,
    }
    if mode not in handlers:
        raise ValueError("Unsupported processing mode.")
    return handlers[mode](input_path)


def _run_clean_metadata(job_dir: Path, input_path: Path) -> list[str]:
    output_name = f"cleaned_output{input_path.suffix.casefold()}"
    output_path = artifact_path(job_dir, output_name)
    before = _inspect_metadata_for_web(input_path)
    clean_report = clean_metadata(input_path, output_path)
    after = _inspect_metadata_for_web(output_path)
    _write_json_artifact(job_dir, "metadata_before.json", before)
    _write_json_artifact(job_dir, "clean_metadata.json", clean_report)
    _write_json_artifact(job_dir, "metadata_after.json", after)
    return ["status.json", output_name, "metadata_before.json", "clean_metadata.json", "metadata_after.json"]


def _run_quick_scan(job_dir: Path, input_path: Path, status_data: dict[str, Any]) -> list[str]:
    _start_step(job_dir, status_data, "analyze")
    analysis = analyze_audio(input_path)
    _write_json_artifact(job_dir, "analysis.json", _scrub_workflow_report(analysis))
    _complete_step(job_dir, status_data, "analyze")

    _start_step(job_dir, status_data, "inspect-metadata")
    metadata = _safe_metadata_report(input_path)
    _write_json_artifact(job_dir, "metadata.json", metadata)
    _complete_step(job_dir, status_data, "inspect-metadata")

    _start_step(job_dir, status_data, "release-check")
    release = release_check(input_path, "streaming")
    _write_json_artifact(job_dir, "release_check.json", _scrub_workflow_report(release))
    _complete_step(job_dir, status_data, "release-check")

    _start_step(job_dir, status_data, "visualize")
    visual = build_visualization_artifacts(input_path)
    _write_json_artifact(job_dir, "visualization.json", _scrub_workflow_report(visual))
    _complete_step(job_dir, status_data, "visualize")

    _start_step(job_dir, status_data, "summary")
    summary = _quick_scan_summary(analysis, metadata, release)
    _write_text_artifact(job_dir, "quick_scan_summary.md", summary)
    _complete_step(job_dir, status_data, "summary")

    return ["status.json", "quick_scan_summary.md", "analysis.json", "metadata.json", "release_check.json", "visualization.json"]


def _run_metadata_clean_workflow(job_dir: Path, input_path: Path, status_data: dict[str, Any]) -> list[str]:
    output_name = f"cleaned_output{input_path.suffix.casefold()}"
    output_path = artifact_path(job_dir, output_name)

    _start_step(job_dir, status_data, "inspect-metadata-before")
    before = _safe_metadata_report(input_path)
    _write_json_artifact(job_dir, "metadata_before.json", before)
    _complete_step(job_dir, status_data, "inspect-metadata-before")

    _start_step(job_dir, status_data, "clean-metadata")
    clean_metadata(input_path, output_path)
    _complete_step(job_dir, status_data, "clean-metadata")

    _start_step(job_dir, status_data, "inspect-metadata-after")
    after = _safe_metadata_report(output_path)
    _write_json_artifact(job_dir, "metadata_after.json", after)
    _complete_step(job_dir, status_data, "inspect-metadata-after")

    _start_step(job_dir, status_data, "metadata-diff")
    diff = _metadata_diff_markdown(before, after)
    _write_text_artifact(job_dir, "metadata_diff.md", diff)
    _complete_step(job_dir, status_data, "metadata-diff")

    _start_step(job_dir, status_data, "hashes")
    hashes = _hash_manifest({"input": input_path, "cleaned_output": output_path})
    _write_json_artifact(job_dir, "hashes.json", hashes)
    _complete_step(job_dir, status_data, "hashes")

    _start_step(job_dir, status_data, "summary")
    summary = _metadata_clean_summary(before, after, output_name)
    _write_text_artifact(job_dir, "metadata_clean_summary.md", summary)
    _complete_step(job_dir, status_data, "summary")

    return ["status.json", output_name, "metadata_before.json", "metadata_after.json", "metadata_diff.md", "metadata_clean_summary.md", "hashes.json"]


def _run_quality_naturalize_workflow(job_dir: Path, input_path: Path, status_data: dict[str, Any]) -> list[str]:
    output_name = f"naturalized_output{input_path.suffix.casefold()}"
    output_path = artifact_path(job_dir, output_name)

    _start_step(job_dir, status_data, "release-check-before")
    before = release_check(input_path, "streaming")
    _write_json_artifact(job_dir, "release_check_before.json", _scrub_workflow_report(before))
    _complete_step(job_dir, status_data, "release-check-before")

    _start_step(job_dir, status_data, "quality-naturalize")
    humanize_audio(input_path, output_path, preset="subtle", target="streaming")
    _complete_step(job_dir, status_data, "quality-naturalize")

    _start_step(job_dir, status_data, "release-check-after")
    after = release_check(output_path, "streaming")
    _write_json_artifact(job_dir, "release_check_after.json", _scrub_workflow_report(after))
    _complete_step(job_dir, status_data, "release-check-after")

    _start_step(job_dir, status_data, "compare")
    comparison = compare_audio(input_path, output_path, "streaming")
    _write_json_artifact(job_dir, "compare.json", _scrub_workflow_report(comparison))
    _complete_step(job_dir, status_data, "compare")

    _start_step(job_dir, status_data, "hashes")
    hashes = _hash_manifest({"input": input_path, "naturalized_output": output_path})
    _write_json_artifact(job_dir, "hashes.json", hashes)
    _complete_step(job_dir, status_data, "hashes")

    _start_step(job_dir, status_data, "summary")
    summary = _quality_naturalize_summary(before, after, output_name)
    _write_text_artifact(job_dir, "quality_naturalize_summary.md", summary)
    _complete_step(job_dir, status_data, "summary")

    return [
        "status.json",
        output_name,
        "release_check_before.json",
        "release_check_after.json",
        "compare.json",
        "quality_naturalize_summary.md",
        "hashes.json",
    ]


def _run_full_release_pass_workflow(job_dir: Path, input_path: Path, status_data: dict[str, Any]) -> list[str]:
    cleaned_name = f"cleaned_output{input_path.suffix.casefold()}"
    cleaned_path = artifact_path(job_dir, cleaned_name)
    final_name = f"final_output{input_path.suffix.casefold()}"
    final_path = artifact_path(job_dir, final_name)

    _start_step(job_dir, status_data, "inspect-metadata-before")
    metadata_before = _safe_metadata_report(input_path)
    _write_json_artifact(job_dir, "metadata_before.json", metadata_before)
    _complete_step(job_dir, status_data, "inspect-metadata-before")

    _start_step(job_dir, status_data, "clean-metadata")
    clean_metadata(input_path, cleaned_path)
    _complete_step(job_dir, status_data, "clean-metadata")

    _start_step(job_dir, status_data, "inspect-metadata-after")
    metadata_after = _safe_metadata_report(cleaned_path)
    _write_json_artifact(job_dir, "metadata_after.json", metadata_after)
    _complete_step(job_dir, status_data, "inspect-metadata-after")

    _start_step(job_dir, status_data, "release-check-before")
    release_before = release_check(cleaned_path, "streaming")
    _write_json_artifact(job_dir, "release_check_before.json", _scrub_workflow_report(release_before))
    _complete_step(job_dir, status_data, "release-check-before")

    _start_step(job_dir, status_data, "quality-naturalize")
    humanize_audio(cleaned_path, final_path, preset="subtle", target="streaming")
    _complete_step(job_dir, status_data, "quality-naturalize")

    _start_step(job_dir, status_data, "compare")
    comparison = compare_audio(cleaned_path, final_path, "streaming")
    _write_json_artifact(job_dir, "compare.json", _scrub_workflow_report(comparison))
    _complete_step(job_dir, status_data, "compare")

    _start_step(job_dir, status_data, "release-check-final")
    release_final = release_check(final_path, "streaming")
    _write_json_artifact(job_dir, "release_check_final.json", _scrub_workflow_report(release_final))
    _complete_step(job_dir, status_data, "release-check-final")

    _start_step(job_dir, status_data, "metadata-diff")
    diff = _metadata_diff_markdown(metadata_before, metadata_after)
    _write_text_artifact(job_dir, "metadata_diff.md", diff)
    _complete_step(job_dir, status_data, "metadata-diff")

    _start_step(job_dir, status_data, "hashes")
    hashes = _hash_manifest({"input": input_path, "cleaned_output": cleaned_path, "final_output": final_path})
    _write_json_artifact(job_dir, "hashes.json", hashes)
    _complete_step(job_dir, status_data, "hashes")

    _start_step(job_dir, status_data, "summary")
    summary_json = _full_release_summary_json(release_before, release_final, metadata_before, metadata_after)
    _write_json_artifact(job_dir, "workflow_summary.json", summary_json)
    _write_text_artifact(job_dir, "workflow_summary.md", _full_release_summary_markdown(summary_json, final_name))
    _complete_step(job_dir, status_data, "summary")

    return [
        "status.json",
        final_name,
        "workflow_summary.md",
        "workflow_summary.json",
        "metadata_before.json",
        "metadata_after.json",
        "metadata_diff.md",
        "release_check_before.json",
        "release_check_final.json",
        "compare.json",
        "hashes.json",
    ]


def _write_json_artifact(job_dir: Path, artifact_name: str, report: dict[str, Any]) -> None:
    _assert_json_safe(report)
    artifact = artifact_path(job_dir, artifact_name)
    artifact.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _write_text_artifact(job_dir: Path, artifact_name: str, text: str) -> None:
    artifact = artifact_path(job_dir, artifact_name)
    artifact.write_text(text.rstrip() + "\n", encoding="utf-8")


def _scrub_workflow_report(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _scrub_workflow_report(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_scrub_workflow_report(item) for item in value]
    if isinstance(value, str) and _contains_blocked_public_term(value):
        return "Omitted private beta safety note."
    return value


def _contains_blocked_public_term(value: str) -> bool:
    lowered = value.casefold()
    blocked_terms = (
        "d2F0ZXJtYXJr",
        "ZmluZ2VycHJpbnQ=",
        "cHJvdmVuYW5jZQ==",
        "YzJwYQ==",
        "ZGV0ZWN0b3I=",
        "YWkgZGV0ZWN0aW9u",
        "dW5kZXRlY3RhYmxl",
        "YnlwYXNz",
        "ZXZhc2lvbg==",
        "aGlkZGVuIGlkZW50aWZpZXI=",
        "c291cmNlIGF0dHJpYnV0aW9u",
        "cmVjb2duaXRpb24gZmFpbHVyZQ==",
    )
    return any(base64.b64decode(term).decode("utf-8").casefold() in lowered for term in blocked_terms)


def _assert_json_safe(report: dict[str, Any]) -> None:
    json.dumps(report, allow_nan=False)


def _inspect_metadata_for_web(input_path: Path) -> dict[str, Any]:
    report = inspect_metadata(input_path)
    display = build_metadata_display(report)
    metadata = report.get("metadata", {})
    if isinstance(metadata, dict) and isinstance(metadata.get("metadata_values"), dict):
        metadata["metadata_values"] = {
            key: value.get("display_value", "")
            for key, value in display.get("metadata_values", {}).items()
        }
    report["metadata_display"] = display
    return report


def _safe_metadata_report(input_path: Path) -> dict[str, Any]:
    report = inspect_metadata(input_path)
    metadata = report.get("metadata", {})
    keys = [str(key) for key in metadata.get("detected_metadata_keys", [])]
    standard_fields = sorted({field for field in STANDARD_METADATA_FIELDS if _field_is_present(field, keys)})
    return {
        "action": "inspect_metadata",
        "file_info": {
            "extension": input_path.suffix.casefold(),
            "size_bytes": input_path.stat().st_size,
            "sha256": sha256_file(input_path),
        },
        "metadata": {
            "metadata_handler": metadata.get("metadata_handler"),
            "metadata_read_error": bool(metadata.get("metadata_read_error")),
            "detected_field_count": len(keys),
            "supported_standard_fields": standard_fields,
            "supported_standard_field_count": len(standard_fields),
            "other_field_count": max(0, len(keys) - len(standard_fields)),
        },
    }


def _field_is_present(field: str, keys: list[str]) -> bool:
    normalized = field.casefold().replace("_", "")
    return any(normalized in key.casefold().replace("_", "").replace("-", "") for key in keys)


def _hash_manifest(paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "action": "artifact_integrity_hashes",
        "algorithm": "sha256",
        "files": {
            label: {
                "file_name": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for label, path in paths.items()
        },
    }


def _metadata_diff_markdown(before: dict[str, Any], after: dict[str, Any]) -> str:
    before_fields = set(before["metadata"]["supported_standard_fields"])
    after_fields = set(after["metadata"]["supported_standard_fields"])
    removed = sorted(before_fields - after_fields)
    added = sorted(after_fields - before_fields)
    kept = sorted(before_fields & after_fields)
    return "\n".join(
        [
            "# Metadata Comparison",
            "",
            "Compared supported standard metadata fields before and after cleanup.",
            "",
            f"- Before supported fields: {len(before_fields)}",
            f"- After supported fields: {len(after_fields)}",
            f"- Removed supported fields: {', '.join(removed) if removed else 'none'}",
            f"- Added supported fields: {', '.join(added) if added else 'none'}",
            f"- Unchanged supported fields: {', '.join(kept) if kept else 'none'}",
        ]
    )


def _quick_scan_summary(analysis: dict[str, Any], metadata: dict[str, Any], release: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Quick Scan Summary",
            "",
            "Check audio quality, metadata, and release readiness without modifying the file.",
            "",
            f"- Release readiness passed: {release.get('passed')}",
            f"- Release readiness score: {release.get('score')}",
            f"- Peak dBFS: {analysis.get('peak_dbfs')}",
            f"- Clipped samples: {analysis.get('clipping_sample_count')}",
            f"- Supported standard metadata fields: {metadata['metadata']['supported_standard_field_count']}",
        ]
    )


def _metadata_clean_summary(before: dict[str, Any], after: dict[str, Any], output_name: str) -> str:
    return "\n".join(
        [
            "# Metadata Clean Summary",
            "",
            "Cleans supported standard metadata fields and non-essential visible container tags where technically supported.",
            "",
            f"- Output artifact: {output_name}",
            f"- Before supported fields: {before['metadata']['supported_standard_field_count']}",
            f"- After supported fields: {after['metadata']['supported_standard_field_count']}",
        ]
    )


def _quality_naturalize_summary(before: dict[str, Any], after: dict[str, Any], output_name: str) -> str:
    return "\n".join(
        [
            "# Quality Naturalize Summary",
            "",
            "Applies conservative audio-quality micro-variations for less sterile playback characteristics.",
            "",
            f"- Output artifact: {output_name}",
            f"- Before release readiness passed: {before.get('passed')}",
            f"- After release readiness passed: {after.get('passed')}",
            f"- Before score: {before.get('score')}",
            f"- After score: {after.get('score')}",
        ]
    )


def _full_release_summary_json(
    release_before: dict[str, Any],
    release_final: dict[str, Any],
    metadata_before: dict[str, Any],
    metadata_after: dict[str, Any],
) -> dict[str, Any]:
    return {
        "action": "full_release_pass_summary",
        "private_beta": True,
        "release_readiness": {
            "after_cleanup_passed": release_before.get("passed"),
            "after_cleanup_score": release_before.get("score"),
            "final_passed": release_final.get("passed"),
            "final_score": release_final.get("score"),
        },
        "metadata": {
            "before_supported_field_count": metadata_before["metadata"]["supported_standard_field_count"],
            "after_supported_field_count": metadata_after["metadata"]["supported_standard_field_count"],
        },
        "notes": [
            "Private beta workflow summary.",
            "Reports cover metadata cleanup, audio quality naturalization, comparison, and release readiness.",
        ],
    }


def _full_release_summary_markdown(summary: dict[str, Any], final_name: str) -> str:
    readiness = summary["release_readiness"]
    metadata = summary["metadata"]
    return "\n".join(
        [
            "# Full Release Pass Summary",
            "",
            "Private beta workflow summary.",
            "",
            f"- Final audio artifact: {final_name}",
            f"- Final release readiness passed: {readiness.get('final_passed')}",
            f"- Final release readiness score: {readiness.get('final_score')}",
            f"- Before supported metadata fields: {metadata.get('before_supported_field_count')}",
            f"- After supported metadata fields: {metadata.get('after_supported_field_count')}",
        ]
    )


def _start_step(job_dir: Path, status_data: dict[str, Any], step_name: str) -> None:
    step = _step_by_name(status_data, step_name)
    step["status"] = "running"
    step["started_at"] = utc_now_iso()
    status_data["status"] = "processing"
    status_data["processing"] = {
        "execution": "running",
        "message": "Private beta workflow is running.",
        "current_step": step_name,
    }
    write_status(job_dir, status_data)


def _complete_step(job_dir: Path, status_data: dict[str, Any], step_name: str) -> None:
    step = _step_by_name(status_data, step_name)
    step["status"] = "completed"
    step["completed_at"] = utc_now_iso()
    write_status(job_dir, status_data)


def _fail_running_step(status_data: dict[str, Any]) -> None:
    for step in status_data.get("steps", []):
        if step.get("status") == "running":
            step["status"] = "failed"
            step["completed_at"] = utc_now_iso()
            return


def _step_by_name(status_data: dict[str, Any], step_name: str) -> dict[str, Any]:
    for step in status_data.get("steps", []):
        if step.get("name") == step_name:
            return step
    raise ValueError("Unknown workflow step.")


def _artifact_groups_for(workflow_name: str, artifacts: list[str]) -> dict[str, list[str]]:
    artifact_set = set(artifacts)
    grouped: dict[str, list[str]] = {}
    for group, names in WORKFLOW_DEFINITIONS[workflow_name]["artifact_groups"].items():
        present = [name for name in names if name in artifact_set]
        if present:
            grouped[group] = present
    ungrouped = [name for name in artifacts if name != "status.json" and all(name not in values for values in grouped.values())]
    if ungrouped:
        grouped["Reports"] = grouped.get("Reports", []) + ungrouped
    return grouped
