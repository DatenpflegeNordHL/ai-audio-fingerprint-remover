from __future__ import annotations

import json

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
    assert data["max_upload_mib"] == 7
    assert data["job_ttl_hours"] == 24
    assert data["partial_ttl_minutes"] == 60
    assert "clean-metadata" in data["single_file_modes"]
    assert "compare" in data["two_file_modes"]
    assert data["deferred_modes"] == ["humanize"]
    encoded = json.dumps(data)
    assert "test-token" not in encoded
    assert str(tmp_path) not in encoded
    assert "AQH_WEB_TOKEN" not in encoded


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
