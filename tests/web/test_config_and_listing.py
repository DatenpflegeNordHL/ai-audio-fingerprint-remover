from __future__ import annotations

import json

from audio_quality_humanizer.web.config import load_config
from audio_quality_humanizer.web.storage import create_job_directory, write_status
from tests.web.helpers import auth_header, call_app, multipart_body, prepare_env


def test_api_config_requires_auth(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/api/config")

    assert response.status_code == 401


def test_api_config_returns_safe_operator_config(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path, max_upload_mib=7)

    response = call_app("GET", "/api/config", headers=auth_header())

    assert response.status_code == 200
    data = response.json()
    assert data["private_beta"] is True
    assert data["web_host"] == "127.0.0.1"
    assert data["web_port"] == 8017
    assert data["max_upload_mib"] == 7
    assert data["job_ttl_hours"] == 24
    assert data["partial_ttl_minutes"] == 60
    assert data["max_active_jobs"] == 1
    assert "clean-metadata" in data["single_file_modes"]
    assert "compare" in data["two_file_modes"]
    assert data["deferred_modes"] == ["humanize"]
    encoded = json.dumps(data)
    assert "test-token" not in encoded
    assert str(tmp_path) not in encoded
    assert "AQH_WEB_TOKEN" not in encoded
    assert "AQH_BETA_PASSWORD" not in encoded


def test_new_deployment_env_names_override_legacy_names(tmp_path, monkeypatch):
    legacy_root = prepare_env(monkeypatch, tmp_path, max_upload_mib=100)
    new_root = tmp_path / "new-jobs"
    monkeypatch.setenv("AQH_WEB_HOST", "127.0.0.1")
    monkeypatch.setenv("AQH_WEB_PORT", "8017")
    monkeypatch.setenv("AQH_WEB_JOBS_DIR", str(new_root))
    monkeypatch.setenv("AQH_WEB_MAX_UPLOAD_MB", "3")
    monkeypatch.setenv("AQH_WEB_JOB_TTL_HOURS", "6")
    monkeypatch.setenv("AQH_WEB_MAX_ACTIVE_JOBS", "2")

    config = load_config()

    assert legacy_root != new_root
    assert config.job_root == new_root
    assert config.max_upload_mib == 3
    assert config.job_ttl_hours == 6
    assert config.max_active_jobs == 2


def test_recent_jobs_endpoint_requires_auth(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/api/jobs")

    assert response.status_code == 401


def test_recent_jobs_endpoint_returns_safe_summaries_newest_first(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    for mode in ("analyze", "release-check"):
        body, content_type = multipart_body(mode=mode)
        upload = call_app(
            "POST",
            "/api/jobs",
            headers={**auth_header(), "content-type": content_type},
            body=body,
        )
        assert upload.status_code == 201

    response = call_app("GET", "/api/jobs", headers=auth_header())

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert [job["mode"] for job in data["jobs"]] == ["release-check", "analyze"]
    for job in data["jobs"]:
        assert set(job).issubset({"job_id", "status", "mode", "created_at", "completed_at", "failed_at", "artifacts"})
        assert "artifacts" in job
    encoded = json.dumps(data)
    assert str(tmp_path) not in encoded
    assert "test-token" not in encoded


def test_active_job_limit_rejects_new_uploads(tmp_path, monkeypatch):
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
            "processing": {"execution": "pending"},
            "artifacts": ["status.json"],
            "safety_notes": [],
        },
    )
    body, content_type = multipart_body(mode="analyze")

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 429
    assert "active job limit" in response.body.decode("utf-8")
