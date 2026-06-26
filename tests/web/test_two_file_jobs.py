from __future__ import annotations

import json

from audio_quality_humanizer.web.config import load_config
from audio_quality_humanizer.web.storage import get_job_directory
from tests.web.helpers import auth_header, call_app, multipart_two_file_body, prepare_env


def test_compare_two_file_job_completes_and_creates_compare_json(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_two_file_body(mode="compare")

    upload = call_app(
        "POST",
        "/api/compare-jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert upload.status_code == 201
    data = upload.json()
    assert data["status"] == "completed"
    assert data["mode"] == "compare"
    assert "inputs" in data
    assert "compare.json" in data["artifacts"]
    job_dir = get_job_directory(load_config(), data["job_id"])
    assert (job_dir / "input" / "before.wav").is_file()
    assert (job_dir / "input" / "after.wav").is_file()
    assert (job_dir / "artifacts" / "compare.json").is_file()

    artifact = call_app("GET", f"/api/jobs/{data['job_id']}/artifacts/compare.json", headers=auth_header())
    assert artifact.status_code == 200
    report = json.loads(artifact.body.decode("utf-8"))
    assert report["action"] == "compare"
    assert "comparison_metrics" in report
    json.dumps(report, allow_nan=False)


def test_visualize_compare_two_file_job_creates_visual_artifacts(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_two_file_body(mode="visualize-compare")

    upload = call_app(
        "POST",
        "/api/compare-jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert upload.status_code == 201
    data = upload.json()
    assert data["status"] == "completed"
    assert "compare.json" in data["artifacts"]
    assert "visual_compare.json" in data["artifacts"]

    artifact = call_app("GET", f"/api/jobs/{data['job_id']}/artifacts/visual_compare.json", headers=auth_header())
    assert artifact.status_code == 200
    report = json.loads(artifact.body.decode("utf-8"))
    assert report["action"] == "visualize-compare"
    assert "difference_map" in report
    json.dumps(report, allow_nan=False)


def test_two_file_endpoint_requires_auth(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_two_file_body()

    response = call_app("POST", "/api/compare-jobs", headers={"content-type": content_type}, body=body)

    assert response.status_code == 401


def test_two_file_endpoint_rejects_unsupported_mode(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_two_file_body(mode="analyze")

    response = call_app(
        "POST",
        "/api/compare-jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 400


def test_two_file_endpoint_rejects_missing_after_file(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    boundary = "aqh-test-boundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="mode"\r\n\r\n'
        "compare\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="before_file"; filename="before.wav"\r\n'
        "Content-Type: audio/wav\r\n\r\n"
        "not-a-real-wav\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")

    response = call_app(
        "POST",
        "/api/compare-jobs",
        headers={**auth_header(), "content-type": f"multipart/form-data; boundary={boundary}"},
        body=body,
    )

    assert response.status_code == 422


def test_two_file_inputs_do_not_use_user_filenames_as_paths(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_two_file_body(
        before_filename="../../before.wav",
        after_filename="../../after.wav",
    )

    upload = call_app(
        "POST",
        "/api/compare-jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert upload.status_code == 201
    data = upload.json()
    job_dir = get_job_directory(load_config(), data["job_id"])
    assert (job_dir / "input" / "before.wav").is_file()
    assert (job_dir / "input" / "after.wav").is_file()
    assert not (tmp_path / "before.wav").exists()
    assert not (tmp_path / "after.wav").exists()
