from __future__ import annotations

import base64
import json
from pathlib import Path

from audio_quality_humanizer.safety import assert_no_unsafe_public_claims
from audio_quality_humanizer.web.config import load_config
from audio_quality_humanizer.web.processing import _artifact_groups_for
from audio_quality_humanizer.web.storage import get_job_directory
import audio_quality_humanizer.web.processing as web_processing
from tests.web.helpers import auth_header, call_app, multipart_body, prepare_env


WORKFLOW_NAMES = ("quick-scan", "metadata-clean", "quality-naturalize", "full-release-pass")


def test_workflow_definitions_are_exposed_in_config(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/api/config", headers=auth_header())

    assert response.status_code == 200
    data = response.json()
    assert tuple(data["workflow_modes"]) == WORKFLOW_NAMES
    assert [item["name"] for item in data["workflows"]] == list(WORKFLOW_NAMES)
    encoded = json.dumps(data)
    assert assert_no_unsafe_public_claims(encoded) == []
    assert "test-token" not in encoded
    assert str(tmp_path) not in encoded


def test_workflow_jobs_complete_with_steps_and_allowlisted_artifacts(tmp_path, monkeypatch):
    expected_artifacts = {
        "quick-scan": {"quick_scan_summary.md", "analysis.json", "metadata.json", "release_check.json", "visualization.json"},
        "metadata-clean": {"cleaned_output.wav", "metadata_before.json", "metadata_after.json", "metadata_diff.md", "metadata_clean_summary.md", "hashes.json"},
        "quality-naturalize": {"naturalized_output.wav", "release_check_before.json", "release_check_after.json", "compare.json", "quality_naturalize_summary.md", "hashes.json"},
        "full-release-pass": {"cleaned_output.wav", "final_output.wav", "workflow_summary.md", "workflow_summary.json", "metadata_before.json", "metadata_after.json", "metadata_diff.md", "release_check_before.json", "release_check_final.json", "compare.json", "hashes.json"},
    }

    for workflow_name in WORKFLOW_NAMES:
        prepare_env(monkeypatch, tmp_path / workflow_name)
        body, content_type = multipart_body(mode=workflow_name)

        response = call_app(
            "POST",
            "/api/jobs",
            headers={**auth_header(), "content-type": content_type},
            body=body,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "completed"
        assert data["mode"] == "workflow"
        assert data["workflow_name"] == workflow_name
        assert {step["status"] for step in data["steps"]} == {"completed"}
        assert expected_artifacts[workflow_name].issubset(set(data["artifacts"]))
        assert set(data["artifact_groups"]).issubset({"Final Audio", "Intermediate Audio", "Reports", "Metadata", "Hashes", "Visuals"})

        job_dir = get_job_directory(load_config(), data["job_id"])
        status_data = json.loads((job_dir / "status.json").read_text(encoding="utf-8"))
        assert status_data["steps"] == data["steps"]
        for artifact_name in data["artifacts"]:
            artifact_path = job_dir / "status.json" if artifact_name == "status.json" else job_dir / "artifacts" / artifact_name
            assert artifact_path.is_file()
        exposed_files = sorted(path.name for path in (job_dir / "artifacts").iterdir() if path.is_file())
        assert sorted(name for name in data["artifacts"] if name != "status.json") == exposed_files

        for artifact_name in data["artifacts"]:
            artifact = call_app(
                "GET",
                f"/api/jobs/{data['job_id']}/artifacts/{artifact_name}",
                headers=auth_header(),
            )
            assert artifact.status_code == 200

        blocked = call_app(
            "GET",
            f"/api/jobs/{data['job_id']}/artifacts/clean_metadata.json",
            headers=auth_header(),
        )
        if workflow_name != "metadata-clean":
            assert blocked.status_code in {400, 404}


def test_full_release_pass_mp3_artifact_groups_are_stable():
    artifacts = [
        "status.json",
        "final_output.mp3",
        "cleaned_output.mp3",
        "workflow_summary.md",
        "workflow_summary.json",
        "metadata_before.json",
        "metadata_after.json",
        "metadata_diff.md",
        "release_check_before.json",
        "release_check_final.json",
        "compare.json",
        "hashes.json",
    ]

    groups = _artifact_groups_for("full-release-pass", artifacts)

    assert groups["Final Audio"] == ["final_output.mp3"]
    assert groups["Intermediate Audio"] == ["cleaned_output.mp3"]
    assert groups["Metadata"] == ["metadata_before.json", "metadata_after.json"]
    assert groups["Hashes"] == ["hashes.json"]
    assert "metadata_before.json" not in groups["Reports"]
    assert "metadata_after.json" not in groups["Reports"]
    assert "hashes.json" not in groups["Reports"]
    assert all(not name.endswith((".wav", ".mp3", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".aif", ".aiff")) for name in groups["Reports"])


def test_existing_single_file_mode_still_works_after_workflow_addition(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body(mode="analyze")

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["mode"] == "analyze"
    assert data["status"] == "completed"
    assert "analysis.json" in data["artifacts"]


def test_workflow_api_requires_token(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body(mode="quick-scan")

    response = call_app("POST", "/api/jobs", headers={"content-type": content_type}, body=body)

    assert response.status_code == 401


def test_failed_workflow_step_returns_safe_status(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    def fail_analysis(_path: Path) -> dict:
        raise RuntimeError(f"internal path {tmp_path} test-token AQH_WEB_TOKEN")

    monkeypatch.setattr(web_processing, "analyze_audio", fail_analysis)
    body, content_type = multipart_body(mode="quick-scan")

    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "failed"
    assert data["processing"]["error_code"] == "workflow_failed"
    assert data["steps"][0]["status"] == "failed"
    encoded = json.dumps(data)
    assert "Traceback" not in encoded
    assert str(tmp_path) not in encoded
    assert "test-token" not in encoded
    assert "AQH_WEB_TOKEN" not in encoded


def test_new_workflow_public_text_uses_safe_terms(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)
    body, content_type = multipart_body(mode="full-release-pass")
    response = call_app(
        "POST",
        "/api/jobs",
        headers={**auth_header(), "content-type": content_type},
        body=body,
    )
    data = response.json()

    fragments = [json.dumps(data)]
    for artifact_name in data["artifacts"]:
        if artifact_name.endswith((".json", ".md")):
            artifact = call_app(
                "GET",
                f"/api/jobs/{data['job_id']}/artifacts/{artifact_name}",
                headers=auth_header(),
            )
            fragments.append(artifact.body.decode("utf-8"))
    page = call_app("GET", "/", headers={"authorization": "Basic " + base64.b64encode(b"beta:secret").decode("ascii")})
    fragments.append(page.body.decode("utf-8"))
    text = "\n".join(fragments)

    assert assert_no_unsafe_public_claims(text) == []
    blocked_terms = [
        base64.b64decode(value).decode("utf-8")
        for value in (
            "d2F0ZXJtYXJr",
            "ZmluZ2VycHJpbnQ=",
            "cHJvdmVuYW5jZQ==",
            "QzJQQQ==",
            "ZGV0ZWN0b3I=",
            "QUkgZGV0ZWN0aW9u",
            "dW5kZXRlY3RhYmxl",
            "YnlwYXNz",
            "ZXZhc2lvbg==",
            "aGlkZGVuIGlkZW50aWZpZXI=",
            "c291cmNlIGF0dHJpYnV0aW9u",
            "cmVjb2duaXRpb24gZmFpbHVyZQ==",
        )
    ]
    lowered = text.casefold()
    for term in blocked_terms:
        assert term.casefold() not in lowered
