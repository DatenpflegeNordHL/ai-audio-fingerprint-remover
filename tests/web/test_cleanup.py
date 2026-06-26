from __future__ import annotations

from datetime import datetime, timezone
import os

from audio_quality_humanizer.web.config import load_config
from audio_quality_humanizer.web.storage import cleanup_expired_jobs, create_job_directory, write_status
from tests.web.helpers import prepare_env


def test_cleanup_removes_expired_job_dirs(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    config = load_config()
    job_dir = create_job_directory(config)
    write_status(
        job_dir,
        {
            "job_id": job_dir.name,
            "status": "uploaded",
            "mode": "analyze",
            "created_at": "2026-01-01T00:00:00+00:00",
            "input": {"extension": ".wav", "size_bytes": 44, "content_type": "audio/wav"},
            "processing": {"execution": "deferred"},
            "artifacts": ["status.json"],
            "safety_notes": [],
        },
    )
    old = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    os.utime(job_dir, (old, old))

    removed = cleanup_expired_jobs(config)

    assert removed == [job_dir.name]
    assert not job_dir.exists()


def test_cleanup_removes_expired_partial_dirs(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    config = load_config()
    job_dir = create_job_directory(config)
    old = datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp()
    os.utime(job_dir, (old, old))

    removed = cleanup_expired_jobs(config)

    assert removed == [job_dir.name]
    assert not job_dir.exists()
