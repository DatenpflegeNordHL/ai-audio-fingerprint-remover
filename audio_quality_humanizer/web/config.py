"""Configuration for the optional private web backend."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


DEFAULT_JOB_ROOT = Path(".var/private-web/jobs")
DEFAULT_WEB_HOST = "127.0.0.1"
DEFAULT_WEB_PORT = 8017
DEFAULT_MAX_UPLOAD_MIB = 50
DEFAULT_JOB_TTL_HOURS = 24
DEFAULT_PARTIAL_TTL_MINUTES = 60
DEFAULT_MAX_ACTIVE_JOBS = 1


@dataclass(frozen=True)
class WebConfig:
    token: str | None
    host: str
    port: int
    job_root: Path
    max_upload_mib: int
    job_ttl_hours: int
    partial_ttl_minutes: int
    max_active_jobs: int
    beta_password: str | None
    beta_password_hash: str | None

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mib * 1024 * 1024


def load_config() -> WebConfig:
    """Load web backend settings from environment variables."""

    return WebConfig(
        token=os.environ.get("AQH_WEB_TOKEN"),
        host=os.environ.get("AQH_WEB_HOST", DEFAULT_WEB_HOST),
        port=_positive_int("AQH_WEB_PORT", DEFAULT_WEB_PORT),
        job_root=Path(_env_value("AQH_WEB_JOBS_DIR", "AQH_WEB_JOB_ROOT", default=str(DEFAULT_JOB_ROOT))),
        max_upload_mib=_positive_int("AQH_WEB_MAX_UPLOAD_MB", DEFAULT_MAX_UPLOAD_MIB, fallback_name="AQH_MAX_UPLOAD_MIB"),
        job_ttl_hours=_positive_int("AQH_WEB_JOB_TTL_HOURS", DEFAULT_JOB_TTL_HOURS, fallback_name="AQH_JOB_TTL_HOURS"),
        partial_ttl_minutes=_positive_int("AQH_PARTIAL_TTL_MINUTES", DEFAULT_PARTIAL_TTL_MINUTES),
        max_active_jobs=_positive_int("AQH_WEB_MAX_ACTIVE_JOBS", DEFAULT_MAX_ACTIVE_JOBS),
        beta_password=os.environ.get("AQH_BETA_PASSWORD"),
        beta_password_hash=os.environ.get("AQH_BETA_PASSWORD_HASH"),
    )


def _env_value(name: str, fallback_name: str | None = None, *, default: str | None = None) -> str:
    value = os.environ.get(name)
    if value is None and fallback_name is not None:
        value = os.environ.get(fallback_name)
    if value is None:
        if default is None:
            raise ValueError(f"{name} is required.")
        return default
    return value


def _positive_int(name: str, default: int, *, fallback_name: str | None = None) -> int:
    value = os.environ.get(name)
    if value is None and fallback_name is not None:
        value = os.environ.get(fallback_name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    return parsed
