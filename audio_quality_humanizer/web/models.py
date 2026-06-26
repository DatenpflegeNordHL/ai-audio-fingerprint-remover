"""Small JSON-safe response builders for the optional private web backend."""

from __future__ import annotations

from typing import Any


SINGLE_FILE_MODES = (
    "analyze",
    "release-check",
    "inspect-metadata",
    "clean-metadata",
    "visualize",
)

TWO_FILE_MODES = (
    "compare",
    "visualize-compare",
)

SUPPORTED_MODES = SINGLE_FILE_MODES + TWO_FILE_MODES

DEFERRED_MODES = (
    "humanize",
)


def health_response() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "audio-quality-humanizer-private-web",
        "private_beta": True,
    }


def job_response(status_data: dict[str, Any]) -> dict[str, Any]:
    response = {
        "job_id": status_data["job_id"],
        "status": status_data["status"],
        "mode": status_data["mode"],
        "created_at": status_data["created_at"],
        "processing": status_data["processing"],
        "artifacts": status_data.get("artifacts", []),
        "safety_notes": status_data.get("safety_notes", []),
    }
    if "input" in status_data:
        response["input"] = _input_response(status_data["input"])
    if "inputs" in status_data:
        response["inputs"] = {
            "before": _input_response(status_data["inputs"]["before"]),
            "after": _input_response(status_data["inputs"]["after"]),
        }
    if status_data.get("completed_at"):
        response["completed_at"] = status_data["completed_at"]
    if status_data.get("failed_at"):
        response["failed_at"] = status_data["failed_at"]
    return response


def _input_response(input_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "extension": input_data["extension"],
        "size_bytes": input_data["size_bytes"],
        "content_type": input_data.get("content_type"),
        "content_type_advisory": input_data.get("content_type_advisory"),
    }


def artifact_metadata_response(job_id: str, artifact_name: str, size_bytes: int) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "artifact_name": artifact_name,
        "size_bytes": size_bytes,
    }
