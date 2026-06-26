"""Synchronous safe single-file processing for the private web backend."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.analysis.release_check import release_check
from audio_quality_humanizer.metadata.cleaner import inspect_metadata
from audio_quality_humanizer.web.storage import artifact_path, read_status, write_status
from audio_quality_humanizer.visualization_artifacts import build_visualization_artifacts


ARTIFACT_BY_MODE = {
    "analyze": "analysis.json",
    "release-check": "release_check.json",
    "inspect-metadata": "metadata.json",
    "visualize": "visualization.json",
}


def execute_job(job_dir: Path, input_path: Path, mode: str) -> dict[str, Any]:
    """Execute a safe single-file mode and update status JSON."""

    status_data = read_status(job_dir)
    try:
        report = _run_mode(input_path, mode)
        _assert_json_safe(report)
        artifact_name = ARTIFACT_BY_MODE[mode]
        artifact = artifact_path(job_dir, artifact_name)
        artifact.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        status_data["status"] = "completed"
        status_data["processing"] = {
            "execution": "completed",
            "message": "Safe single-file processing completed.",
        }
        status_data["artifacts"] = ["status.json", artifact_name]
    except Exception:
        status_data["status"] = "failed"
        status_data["processing"] = {
            "execution": "failed",
            "message": "Processing failed safely.",
            "error_code": "processing_failed",
        }
        status_data["artifacts"] = ["status.json"]
    write_status(job_dir, status_data)
    return status_data


def _run_mode(input_path: Path, mode: str) -> dict[str, Any]:
    handlers: dict[str, Callable[[Path], dict[str, Any]]] = {
        "analyze": analyze_audio,
        "release-check": lambda path: release_check(path, "streaming"),
        "inspect-metadata": inspect_metadata,
        "visualize": build_visualization_artifacts,
    }
    if mode not in handlers:
        raise ValueError("Unsupported processing mode.")
    return handlers[mode](input_path)


def _assert_json_safe(report: dict[str, Any]) -> None:
    json.dumps(report, allow_nan=False)
