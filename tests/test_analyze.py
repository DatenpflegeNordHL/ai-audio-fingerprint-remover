from __future__ import annotations

import numpy as np
import soundfile as sf

from audio_quality_humanizer.analysis.metrics import analyze_audio


def test_analyze_audio_returns_required_metrics(tmp_path):
    input_path = tmp_path / "sine.wav"
    samplerate = 48000
    duration = 1.0
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = 0.25 * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(input_path, audio, samplerate)

    report = analyze_audio(input_path)

    assert report["samplerate"] == samplerate
    assert report["duration_seconds"] == duration
    assert "peak_dbfs" in report
    assert "rms_dbfs" in report
    assert "loudness_lufs_approx" in report
    assert "crest_factor_db" in report
    assert "clipping_sample_count" in report
    assert report["guardrails"]["input_valid"] is True
    assert report["guardrails"]["samplerate_valid"] is True
    assert isinstance(report["warnings"], list)


def test_analyze_audio_returns_stereo_metrics(tmp_path):
    input_path = tmp_path / "stereo.wav"
    samplerate = 48000
    t = np.linspace(0.0, 1.0, samplerate, endpoint=False)
    left = 0.25 * np.sin(2.0 * np.pi * 440.0 * t)
    right = 0.20 * np.sin(2.0 * np.pi * 440.0 * t + 0.1)
    sf.write(input_path, np.column_stack([left, right]), samplerate)

    report = analyze_audio(input_path)

    assert report["channels"] == 2
    assert "stereo_correlation" in report
    assert "side_energy_ratio" in report
    assert "mono_compatibility_warning" in report
    assert "low_end_stereo_warning" in report


def test_clipped_audio_adds_warning(tmp_path):
    input_path = tmp_path / "clipped.wav"
    samplerate = 48000
    audio = np.ones(samplerate, dtype=np.float64)
    sf.write(input_path, audio, samplerate, subtype="FLOAT")

    report = analyze_audio(input_path)

    assert report["clipping_sample_count"] > 0
    assert any("Clipping detected" in warning for warning in report["warnings"])
