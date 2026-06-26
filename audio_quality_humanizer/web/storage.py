"""Temporary job storage helpers for the optional private web backend."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import secrets
import shutil
from typing import Any

from fastapi import HTTPException, status

from audio_quality_humanizer.web.config import WebConfig


JOB_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{22,}$")
ARTIFACT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
ALLOWED_ARTIFACT_NAMES = {
    "status.json",
    "analysis.json",
    "release_check.json",
    "release_check_before.json",
    "release_check_after.json",
    "release_check_final.json",
    "metadata.json",
    "metadata_before.json",
    "metadata_after.json",
    "clean_metadata.json",
    "metadata_diff.md",
    "metadata_clean_summary.md",
    "quick_scan_summary.md",
    "quality_naturalize_summary.md",
    "workflow_summary.md",
    "workflow_summary.json",
    "hashes.json",
    "compare.json",
    "visualization.json",
    "visual_compare.json",
}
ALLOWED_ARTIFACT_NAMES.update(
    {
        f"cleaned_output{extension}"
        for extension in (".wav", ".flac", ".mp3", ".m4a", ".aac", ".ogg", ".opus", ".aif", ".aiff")
    }
)
ALLOWED_ARTIFACT_NAMES.update(
    {
        f"naturalized_output{extension}"
        for extension in (".wav", ".flac", ".mp3", ".m4a", ".aac", ".ogg", ".opus", ".aif", ".aiff")
    }
)
ALLOWED_ARTIFACT_NAMES.update(
    {
        f"final_output{extension}"
        for extension in (".wav", ".flac", ".mp3", ".m4a", ".aac", ".ogg", ".opus", ".aif", ".aiff")
    }
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def generate_job_id() -> str:
    return secrets.token_urlsafe(24)


def resolve_job_root(config: WebConfig) -> Path:
    root = config.job_root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def create_job_directory(config: WebConfig, job_id: str | None = None) -> Path:
    root = resolve_job_root(config)
    for _ in range(10):
        candidate_id = job_id or generate_job_id()
        if not is_valid_job_id(candidate_id):
            raise ValueError("Invalid job id.")
        job_dir = safe_child(root, candidate_id)
        if not job_dir.exists():
            (job_dir / "input").mkdir(parents=True)
            (job_dir / "artifacts").mkdir()
            return job_dir
        if job_id is not None:
            raise FileExistsError(f"Job already exists: {job_id}")
    raise RuntimeError("Unable to create a unique job id.")


def is_valid_job_id(value: str) -> bool:
    return bool(JOB_ID_PATTERN.fullmatch(value)) and "/" not in value and "\\" not in value and "." not in value


def safe_child(root: Path, *parts: str) -> Path:
    resolved_root = root.resolve()
    candidate = resolved_root.joinpath(*parts).resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid path.")
    return candidate


def get_job_directory(config: WebConfig, job_id: str) -> Path:
    if not is_valid_job_id(job_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    job_dir = safe_child(resolve_job_root(config), job_id)
    if not job_dir.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return job_dir


def input_path_for(job_dir: Path, extension: str) -> Path:
    return safe_child(job_dir / "input", f"upload{extension.casefold()}")


def named_input_path_for(job_dir: Path, stem: str, extension: str) -> Path:
    if stem not in {"before", "after"}:
        raise ValueError("Unsupported input stem.")
    return safe_child(job_dir / "input", f"{stem}{extension.casefold()}")


def write_status(job_dir: Path, status_data: dict[str, Any]) -> Path:
    path = safe_child(job_dir, "status.json")
    path.write_text(json.dumps(status_data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_status(job_dir: Path) -> dict[str, Any]:
    path = safe_child(job_dir, "status.json")
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job status not found.")
    return json.loads(path.read_text(encoding="utf-8"))


def list_job_summaries(config: WebConfig, limit: int = 25) -> list[dict[str, Any]]:
    root = resolve_job_root(config)
    summaries: list[tuple[str, float, dict[str, Any]]] = []
    for child in root.iterdir():
        if not child.is_dir() or not is_valid_job_id(child.name):
            continue
        status_path = child / "status.json"
        if not status_path.is_file():
            continue
        try:
            status_data = json.loads(status_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        summaries.append((status_data.get("created_at") or "", status_path.stat().st_mtime, _job_summary(status_data)))
    summaries.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [summary for _, _, summary in summaries[:limit]]


def active_job_count(config: WebConfig) -> int:
    return sum(1 for summary in list_job_summaries(config, limit=10_000) if summary.get("status") in {"uploaded", "processing"})


def _job_summary(status_data: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "job_id": status_data.get("job_id"),
        "status": status_data.get("status"),
        "mode": status_data.get("mode"),
        "created_at": status_data.get("created_at"),
        "artifacts": list(status_data.get("artifacts", [])),
    }
    if status_data.get("completed_at"):
        summary["completed_at"] = status_data["completed_at"]
    if status_data.get("failed_at"):
        summary["failed_at"] = status_data["failed_at"]
    if status_data.get("workflow_name"):
        summary["workflow_name"] = status_data["workflow_name"]
    if status_data.get("workflow_label"):
        summary["workflow_label"] = status_data["workflow_label"]
    return summary


def artifact_path(job_dir: Path, artifact_name: str) -> Path:
    if (
        artifact_name not in ALLOWED_ARTIFACT_NAMES
        or not ARTIFACT_NAME_PATTERN.fullmatch(artifact_name)
        or "/" in artifact_name
        or "\\" in artifact_name
        or ".." in artifact_name
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid artifact name.")
    if artifact_name == "status.json":
        return safe_child(job_dir, "status.json")
    return safe_child(job_dir / "artifacts", artifact_name)


def delete_job(config: WebConfig, job_id: str) -> bool:
    job_dir = get_job_directory(config, job_id)
    shutil.rmtree(job_dir)
    return True


def cleanup_expired_jobs(config: WebConfig, now: datetime | None = None) -> list[str]:
    root = resolve_job_root(config)
    now = now or datetime.now(timezone.utc)
    removed: list[str] = []
    job_ttl_seconds = config.job_ttl_hours * 60 * 60
    partial_ttl_seconds = config.partial_ttl_minutes * 60

    for child in root.iterdir():
        if not child.is_dir():
            continue
        if not is_valid_job_id(child.name):
            continue
        status_path = child / "status.json"
        ttl_seconds = job_ttl_seconds if status_path.exists() else partial_ttl_seconds
        age_seconds = now.timestamp() - child.stat().st_mtime
        if age_seconds > ttl_seconds:
            shutil.rmtree(child)
            removed.append(child.name)
    return removed
