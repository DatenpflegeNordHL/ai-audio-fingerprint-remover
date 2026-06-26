from __future__ import annotations

from audio_quality_humanizer.safety import assert_no_unsafe_public_claims
from tests.web.helpers import call_app, prepare_env


def test_operator_page_returns_useful_private_beta_html(tmp_path, monkeypatch):
    prepare_env(monkeypatch, tmp_path)

    response = call_app("GET", "/")

    assert response.status_code == 200
    html = response.body.decode("utf-8")
    assert "Audio Quality Humanizer" in html
    assert "Private beta / local" in html
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
    assert "Safety / FAQ" in html
    assert "Preview result" in html
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
