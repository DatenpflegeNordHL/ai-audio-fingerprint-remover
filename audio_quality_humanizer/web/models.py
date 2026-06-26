"""Small JSON-safe response builders for the optional private web backend."""

from __future__ import annotations

from typing import Any


SUPPORTED_MODES = (
    "analyze",
    "release-check",
    "inspect-metadata",
    "clean-metadata",
    "visualize",
)

DEFERRED_MODES = (
    "visualize-compare",
    "compare",
    "humanize",
)


def health_response() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "audio-quality-humanizer-private-web",
        "private_beta": True,
    }


def job_response(status_data: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": status_data["job_id"],
        "status": status_data["status"],
        "mode": status_data["mode"],
        "created_at": status_data["created_at"],
        "input": {
            "extension": status_data["input"]["extension"],
            "size_bytes": status_data["input"]["size_bytes"],
            "content_type": status_data["input"].get("content_type"),
        },
        "processing": status_data["processing"],
        "artifacts": status_data.get("artifacts", []),
        "safety_notes": status_data.get("safety_notes", []),
    }


def artifact_metadata_response(job_id: str, artifact_name: str, size_bytes: int) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "artifact_name": artifact_name,
        "size_bytes": size_bytes,
    }
