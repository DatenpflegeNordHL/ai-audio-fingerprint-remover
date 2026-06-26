"""Configuration for the optional private web backend."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


DEFAULT_JOB_ROOT = Path(".var/private-web/jobs")
DEFAULT_MAX_UPLOAD_MIB = 100
DEFAULT_JOB_TTL_HOURS = 24
DEFAULT_PARTIAL_TTL_MINUTES = 60


@dataclass(frozen=True)
class WebConfig:
    token: str | None
    job_root: Path
    max_upload_mib: int
    job_ttl_hours: int
    partial_ttl_minutes: int

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mib * 1024 * 1024


def load_config() -> WebConfig:
    """Load web backend settings from environment variables."""

    return WebConfig(
        token=os.environ.get("AQH_WEB_TOKEN"),
        job_root=Path(os.environ.get("AQH_WEB_JOB_ROOT", str(DEFAULT_JOB_ROOT))),
        max_upload_mib=_positive_int("AQH_MAX_UPLOAD_MIB", DEFAULT_MAX_UPLOAD_MIB),
        job_ttl_hours=_positive_int("AQH_JOB_TTL_HOURS", DEFAULT_JOB_TTL_HOURS),
        partial_ttl_minutes=_positive_int("AQH_PARTIAL_TTL_MINUTES", DEFAULT_PARTIAL_TTL_MINUTES),
    )


def _positive_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return parsed
