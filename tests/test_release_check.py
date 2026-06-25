from __future__ import annotations

import pytest
import numpy as np
import soundfile as sf

from audio_quality_humanizer.analysis.release_check import release_check


def _write_sine(path, amplitude=0.2, samplerate=48000):
    t = np.linspace(0.0, 1.0, samplerate, endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate)


def test_clean_sine_release_check_returns_target_and_score(tmp_path):
    input_path = tmp_path / "sine.wav"
    _write_sine(input_path)

    report = release_check(input_path, target="streaming")

    assert report["action"] == "release_check"
    assert report["target"] == "streaming"
    assert isinstance(report["score"], int)
    assert 0 <= report["score"] <= 100


def test_clipped_audio_creates_blocking_issue(tmp_path):
    input_path = tmp_path / "clipped.wav"
    sf.write(input_path, np.ones(48000, dtype=np.float64), 48000, subtype="FLOAT")

    report = release_check(input_path, target="streaming")

    assert report["blocking_issues"]
    assert any("Clipping" in issue for issue in report["blocking_issues"])
    assert report["passed"] is False


def test_club_target_includes_low_end_stereo_recommendation(tmp_path):
    input_path = tmp_path / "club.wav"
    _write_sine(input_path, amplitude=0.2)

    report = release_check(input_path, target="club")

    combined = " ".join(report["warnings"] + report["recommendations"]).casefold()
    assert "low-end" in combined or "stereo" in combined


def test_invalid_target_raises_clear_error(tmp_path):
    input_path = tmp_path / "sine.wav"
    _write_sine(input_path)

    with pytest.raises(ValueError, match="Unsupported release-check target"):
        release_check(input_path, target="invalid")
