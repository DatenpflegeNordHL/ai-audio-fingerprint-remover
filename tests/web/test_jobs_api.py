from __future__ import annotations

import json
import math

from audio_quality_humanizer.safety import assert_no_unsafe_public_claims
from audio_quality_humanizer.web.config import load_config
from audio_quality_humanizer.web.storage import get_job_directory
import audio_quality_humanizer.web.processing as web_processing
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


def test_safe_single_file_modes_generate_downloadable_artifacts(tmp_path, monkeypatch):
    expected = {
        "analyze": "analysis.json",
        "release-check": "release_check.json",
        "inspect-metadata": "metadata.json",
        "clean-metadata": "clean_metadata.json",
        "visualize": "visualization.json",
    }

    for mode, artifact_name in expected.items():
        prepare_env(monkeypatch, tmp_path / mode)
        body, content_type = multipart_body(mode=mode)
        upload = call_app(
            "POST",
            "/api/jobs",
            headers={**auth_header(), "content-type": content_type},
            body=body,
        )

        assert upload.status_code == 201
        data = upload.json()
        assert data["status"] == "completed"
        assert artifact_name in data["artifacts"]
        if mode == "clean-metadata":
            assert "cleaned_output.wav" in data["artifacts"]
            assert "metadata_before.json" in data["artifacts"]
            assert "metadata_after.json" in data["artifacts"]
        job_dir = get_job_directory(load_config(), data["job_id"])
        assert (job_dir / "artifacts" / artifact_name).is_file()
        assert job_dir.resolve() in (job_dir / "artifacts" / artifact_name).resolve().parents

        artifact = call_app(
            "GET",
            f"/api/jobs/{data['job_id']}/artifacts/{artifact_name}",
            headers=auth_header(),
        )
        assert artifact.status_code == 200
        report = json.loads(artifact.body.decode("utf-8"))
        json.dumps(report, allow_nan=False)
        if mode == "visualize":
            assert "waveform_peaks" in report
            assert "peaks" in report["waveform_peaks"]
            assert "spectrogram" in report
            assert "energy_db" in report["spectrogram"]


def test_inspect_metadata_artifact_includes_sanitized_display(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    huge_cover = "binary-cover-data-" * 1000
    long_title = "long title " * 200

    def fake_metadata(_path):
        return {
            "action": "inspect_metadata",
            "file_info": {"path": "input.mp3", "extension": ".mp3", "size_bytes": 100, "sha256": "abc"},
            "warnings": [],
            "metadata": {
                "metadata_handler": "synthetic",
                "metadata_read_error": None,
                "detected_metadata_keys": ["APIC:Cover", "title"],
                "metadata_values": {
                    "APIC:Cover": huge_cover,
                    "title": long_title,
                },
                "ordinary_metadata_keys": ["APIC:Cover", "title"],
                "possible_provenance_keys": [],
                "warnings": [],
            },
        }

    monkeypatch.setattr(web_processing, "inspect_metadata", fake_metadata)
    body, content_type = multipart_body(mode="inspect-metadata")
    upload = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert upload.status_code == 201
    job_id = upload.json()["job_id"]
    artifact = call_app("GET", f"/api/jobs/{job_id}/artifacts/metadata.json", headers=auth_header())
    report = json.loads(artifact.body.decode("utf-8"))
    display = report["metadata_display"]

    assert display["detected_metadata_keys"] == ["APIC:Cover", "title"]
    assert display["metadata_values"]["APIC:Cover"]["embedded_cover"] is True
    assert display["metadata_values"]["APIC:Cover"]["display_value"] == "[embedded image omitted]"
    assert huge_cover not in json.dumps(display)
    assert huge_cover not in json.dumps(report)
    assert report["metadata"]["metadata_values"]["APIC:Cover"] == "[embedded image omitted]"
    assert display["metadata_values"]["title"]["truncated"] is True
    assert len(display["metadata_values"]["title"]["display_value"]) <= 503


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


def test_deferred_modes_are_rejected(tmp_path, monkeypatch):
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


def test_clean_metadata_web_job_creates_output_and_preserves_input(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body(mode="clean-metadata")

    upload = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert upload.status_code == 201
    data = upload.json()
    assert data["status"] == "completed"
    assert {"cleaned_output.wav", "metadata_before.json", "clean_metadata.json", "metadata_after.json"}.issubset(data["artifacts"])
    job_dir = get_job_directory(load_config(), data["job_id"])
    assert (job_dir / "input" / "upload.wav").is_file()
    assert (job_dir / "artifacts" / "cleaned_output.wav").is_file()
    assert (job_dir / "artifacts" / "cleaned_output.wav").read_bytes() == (job_dir / "input" / "upload.wav").read_bytes()

    artifact = call_app(
        "GET",
        f"/api/jobs/{data['job_id']}/artifacts/cleaned_output.wav",
        headers=auth_header(),
    )
    assert artifact.status_code == 200
    assert artifact.headers["content-type"].startswith("audio/wav")

    clean_report = call_app(
        "GET",
        f"/api/jobs/{data['job_id']}/artifacts/clean_metadata.json",
        headers=auth_header(),
    )
    encoded = clean_report.body.decode("utf-8")
    assert assert_no_unsafe_public_claims(encoded) == []
    json.dumps(json.loads(encoded), allow_nan=False)


def test_failed_processing_returns_safe_status_without_traceback(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    def fail_analysis(_path):
        raise RuntimeError(f"internal failure details {tmp_path} test-token AQH_WEB_TOKEN")

    monkeypatch.setattr(web_processing, "analyze_audio", fail_analysis)
    body, content_type = multipart_body(mode="analyze")

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "failed"
    encoded = json.dumps(data)
    assert "Traceback" not in encoded
    assert "internal failure details" not in encoded
    assert str(tmp_path) not in encoded
    assert "test-token" not in encoded
    assert "AQH_WEB_TOKEN" not in encoded
    assert data["processing"]["error_code"] == "processing_failed"

    status_artifact = call_app(
        "GET",
        f"/api/jobs/{data['job_id']}/artifacts/status.json",
        headers=auth_header(),
    )
    status_encoded = status_artifact.body.decode("utf-8")
    assert "Traceback" not in status_encoded
    assert str(tmp_path) not in status_encoded
    assert "test-token" not in status_encoded


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
