from __future__ import annotations

from audio_quality_humanizer.safety import assert_no_unsafe_public_claims
from tests.web.helpers import call_app, prepare_env


def test_operator_page_returns_useful_private_beta_html(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/")

    assert response.status_code == 200
    html = response.body.decode("utf-8")
    assert "Audio Quality Humanizer" in html
    assert "Local private beta" in html
    assert "Do not expose directly to the public internet" in html
    assert "Bearer token" in html
    assert "before-file" in html
    assert "after-file" in html
    assert "/api/compare-jobs" in html
    assert "Create job" in html
    assert "Job Status" in html
    assert "Artifacts" in html
    assert "Metric Cards" in html
    assert "Visualization Preview" in html
    assert "Metadata" in html
    assert "Raw JSON Preview" in html
    assert "Operator" in html
    assert "Run cleanup" in html
    assert "Recent Jobs" in html
    assert "/api/config" in html
    assert "/api/jobs" in html
    assert "/api/maintenance/cleanup" in html
    assert "Safety / FAQ" in html
    assert "Preview result" in html
    assert "Preview is not available for this artifact type. Download the artifact instead." in html
    assert "function artifactLabel" in html
    assert "function normalizeArtifactName" in html
    assert "function loadJobStatus" in html
    assert "function renderCompletedJob" in html
    assert "function messageForStatus" in html
    assert "function networkFailureMessage" in html
    assert "function extractJobId" in html
    assert "Job status request failed." in html
    assert "Job list request failed." in html
    assert "Config request failed." in html
    assert "Artifact preview request failed." in html
    assert "The job was created, but the response did not include a job id. Refresh the job list." in html
    assert "The job was created, but the dashboard could not render the updated job view. Refresh the job list." in html
    assert "Artifact rendering failed. Download buttons may be incomplete. Refresh the job list." in html
    assert "Bearer token is missing or invalid." in html
    assert "This job no longer exists or has expired." in html
    assert "The submitted data was invalid." in html
    assert "The server could not complete the request. Check logs." in html
    assert "The request could not reach the private beta API." in html
    assert "Request failed safely." not in html
    assert "result.textContent = `Artifact preview" not in html
    assert "rawJson.textContent = `Artifact preview" in html
    assert "rawJson.textContent = 'Artifact rendering failed" in html
    assert "Download ${label}" in html
    assert "Preview ${label}" in html
    assert "Waveform preview" in html
    assert "Spectrogram energy preview" in html
    assert "analyze" in html
    assert "release-check" in html
    assert "inspect-metadata" in html
    assert "visualize" in html
    assert "clean-metadata" in html
    assert "compare" in html
    assert "visualize-compare" in html
    assert "localStorage" not in html
    assert "sessionStorage" not in html
    assert "document.cookie" not in html
    assert "http://" not in html
    assert "https://" not in html
    for fake in ("Naturalness", "Rauschreduktion", "noise reduction", "undetectable"):
        assert fake not in html
    assert assert_no_unsafe_public_claims(html) == []


def test_operator_page_separates_create_job_success_from_followup_errors(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/")

    assert response.status_code == 200
    html = response.body.decode("utf-8")
    assert html.count("Create job request failed.") == 2
    assert "if (!response.ok)" in html
    assert "payload = await response.json();" in html
    assert "const jobId = extractJobId(payload);" in html
    assert "setJobStatusMessage(JSON.stringify(payload, null, 2));" in html
    assert "await loadJobList();" in html
    assert "await loadJobStatus(jobId);" in html
    assert "await loadConfig();" in html
    assert "Job status request failed." in html
    assert "The job was created, but the dashboard could not render the updated job view. Refresh the job list." in html
    assert "Artifact preview request failed." in html
    assert "Artifact rendering failed. Download buttons may be incomplete. Refresh the job list." in html
