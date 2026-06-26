from __future__ import annotations

from audio_quality_humanizer.web.config import load_config
from audio_quality_humanizer.web.storage import artifact_path, get_job_directory, is_valid_job_id, read_status
from tests.web.helpers import auth_header, call_app, multipart_body, prepare_env


def test_filename_traversal_does_not_escape_storage(tmp_path, monkeypatch):
    job_root = prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body(filename="../../evil.wav")

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 201
    job_id = response.json()["job_id"]
    job_dir = get_job_directory(load_config(), job_id)
    assert job_root.resolve() in job_dir.resolve().parents
    assert (job_dir / "input" / "upload.wav").is_file()
    assert not (tmp_path / "evil.wav").exists()
    assert "../../evil.wav" not in read_status(job_dir)["input"].values()


def test_job_id_is_random_looking_and_not_path_like(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body()

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    job_id = response.json()["job_id"]
    assert is_valid_job_id(job_id)
    assert "/" not in job_id
    assert "\\" not in job_id
    assert "." not in job_id
    assert len(job_id) >= 22


def test_artifact_access_cannot_use_parent_segments(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body()
    upload = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )
    job_id = upload.json()["job_id"]

    response = call_app(
        "GET",
        f"/api/jobs/{job_id}/artifacts/../status.json",
        headers=auth_header(),
    )

    assert response.status_code == 400
    job_dir = get_job_directory(load_config(), job_id)
    try:
        artifact_path(job_dir, "../status.json")
    except Exception as exc:
        assert "Invalid artifact name" in str(exc)
    else:
        raise AssertionError("Traversal artifact path was accepted.")
