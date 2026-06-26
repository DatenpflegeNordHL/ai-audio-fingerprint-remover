from __future__ import annotations

import json
import math

from audio_quality_humanizer.safety import assert_no_unsafe_public_claims
from tests.web.helpers import auth_header, call_app, multipart_body, prepare_env


def _walk_values(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_values(item)
    else:
        yield value


def test_job_status_round_trip_is_json_safe_and_safe_worded(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body(mode="visualize")
    upload = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert upload.status_code == 201
    job_id = upload.json()["job_id"]
    status = call_app("GET", f"/api/jobs/{job_id}", headers=auth_header())

    assert status.status_code == 200
    data = status.json()
    encoded = json.dumps(data, allow_nan=False)
    assert assert_no_unsafe_public_claims(encoded) == []
    for value in _walk_values(data):
        if isinstance(value, float):
            assert math.isfinite(value)


def test_status_artifact_can_be_downloaded(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body()
    upload = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )
    job_id = upload.json()["job_id"]

    response = call_app("GET", f"/api/jobs/{job_id}/artifacts/status.json", headers=auth_header())

    assert response.status_code == 200
    assert json.loads(response.body.decode("utf-8"))["job_id"] == job_id


def test_unsupported_modes_are_rejected(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    for mode in ("visualize-compare", "compare", "humanize"):
        body, content_type = multipart_body(mode=mode)
        response = call_app(
            "POST",
            "/api/jobs",
            headers={**auth_header(), "content-type": content_type},
            body=body,
        )
        assert response.status_code == 400


def test_delete_job_removes_directory(tmp_path, monkeypatch):
    job_root = prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body()
    upload = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )
    job_id = upload.json()["job_id"]

    response = call_app("DELETE", f"/api/jobs/{job_id}", headers=auth_header())

    assert response.status_code == 200
    assert response.json()["deleted"] is True
    assert not (job_root / job_id).exists()
