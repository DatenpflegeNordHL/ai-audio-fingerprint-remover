from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audio_quality_humanizer.analysis.compare import compare_audio
from audio_quality_humanizer.cli import main
from audio_quality_humanizer.reports.markdown_report import write_markdown_report
from audio_quality_humanizer.safety import assert_no_unsafe_public_claims


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_METRIC_NAMES = (
    "watermark_score",
    "fingerprint_score",
    "detector_score",
    "evasion_score",
    "bypass_score",
    "recognition_score",
    "provenance_score",
    "detectability_score",
    "origin_score",
    "source_attribution_score",
)


def _write_sine(path, *, amplitude=0.2, samplerate=48000, duration=1.0, frequency=440.0):
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * frequency * t)
    sf.write(path, audio, samplerate)


def _walk_values(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_values(item)
    else:
        yield value


def test_compare_identical_file_passes_with_tiny_difference(tmp_path):
    input_path = tmp_path / "sine.wav"
    _write_sine(input_path)

    report = compare_audio(input_path, input_path)

    assert report["passed"] is True
    assert report["score"] >= 95
    assert report["waveform_similarity"]["likely_identical_audio"] is True
    assert report["waveform_similarity"]["rms_difference"] == 0.0
    metrics = report["comparison_metrics"]
    assert metrics["rmse"] == 0.0
    assert metrics["mean_absolute_error"] == 0.0
    assert metrics["peak_delta"] == 0.0
    assert metrics["rms_delta"] == 0.0
    assert metrics["dynamic_range_delta_db"] == 0.0
    assert metrics["spectral_centroid_delta_hz"] == 0.0
    assert metrics["spectral_rolloff_delta_hz"] == 0.0


def test_compare_gain_changed_file_populates_neutral_metrics(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path, amplitude=0.2)
    _write_sine(candidate_path, amplitude=0.1)

    metrics = compare_audio(reference_path, candidate_path)["comparison_metrics"]

    assert metrics["rmse"] > 0.0
    assert metrics["mean_absolute_error"] > 0.0
    assert metrics["correlation"] > 0.99
    assert metrics["peak_after"] < metrics["peak_before"]
    assert metrics["rms_after"] < metrics["rms_before"]
    assert metrics["rms_delta"] < 0.0


def test_compare_clipped_candidate_is_regression(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path, amplitude=0.2)
    sf.write(candidate_path, np.ones(48000, dtype=np.float64), 48000, subtype="FLOAT")

    report = compare_audio(reference_path, candidate_path)

    messages = " ".join(item["message"] for item in report["regressions"])
    assert "clipping" in messages.casefold()
    assert report["passed"] is False
    assert report["score"] < 100
    assert report["comparison_metrics"]["peak_after"] >= 1.0
    assert report["comparison_metrics"]["peak_delta"] > 0.0


def test_compare_silent_input_does_not_crash_and_uses_json_nulls(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    sf.write(reference_path, np.zeros(48000, dtype=np.float64), 48000)
    sf.write(candidate_path, np.zeros(48000, dtype=np.float64), 48000)

    report = compare_audio(reference_path, candidate_path)
    metrics = report["comparison_metrics"]

    assert metrics["rmse"] == 0.0
    assert metrics["mean_absolute_error"] == 0.0
    assert metrics["correlation"] == 1.0
    assert metrics["snr_db_approx"] is None
    json.dumps(report, allow_nan=False)


def test_compare_duration_mismatch_is_regression(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path, duration=1.0)
    _write_sine(candidate_path, duration=1.5)

    report = compare_audio(reference_path, candidate_path)

    assert report["compatibility"]["duration_match_within_100ms"] is False
    assert any("duration differs" in item["message"] for item in report["regressions"])


def test_compare_samplerate_mismatch_skips_waveform_similarity(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path, samplerate=44100)
    _write_sine(candidate_path, samplerate=48000)

    report = compare_audio(reference_path, candidate_path)

    assert report["compatibility"]["samplerate_match"] is False
    assert report["waveform_similarity"]["rms_difference"] is None
    assert report["waveform_similarity"]["comparison_method"] == "skipped_samplerate_mismatch"
    assert any("Sample rates differ" in warning for warning in report["warnings"])


def test_compare_mono_stereo_shape_difference_uses_safe_downmix(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    samplerate = 48000
    t = np.linspace(0.0, 1.0, samplerate, endpoint=False)
    mono = 0.2 * np.sin(2.0 * np.pi * 440.0 * t)
    stereo = np.column_stack([mono, mono])
    sf.write(reference_path, mono, samplerate)
    sf.write(candidate_path, stereo, samplerate)

    report = compare_audio(reference_path, candidate_path)

    assert report["compatibility"]["channels_match"] is False
    assert report["waveform_similarity"]["comparison_method"] == "mono_downmix_channel_mismatch"
    assert report["comparison_metrics"]["rmse"] == 0.0


def test_compare_spectral_change_is_reflected_in_metrics(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path, frequency=220.0)
    _write_sine(candidate_path, frequency=2200.0)

    metrics = compare_audio(reference_path, candidate_path)["comparison_metrics"]

    assert abs(metrics["spectral_centroid_delta_hz"]) > 500.0
    assert abs(metrics["spectral_rolloff_delta_hz"]) > 500.0


def test_compare_report_is_json_safe_and_uses_safe_metric_names(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path)
    _write_sine(candidate_path, amplitude=0.12)

    report = compare_audio(reference_path, candidate_path)
    encoded = json.dumps(report, allow_nan=False)

    for value in _walk_values(report):
        if isinstance(value, float):
            assert math.isfinite(value)
    for forbidden_name in FORBIDDEN_METRIC_NAMES:
        assert forbidden_name not in encoded


def test_compare_report_contains_required_metric_keys(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path)
    _write_sine(candidate_path, amplitude=0.12)

    metrics = compare_audio(reference_path, candidate_path)["comparison_metrics"]

    for key in (
        "rmse",
        "mean_absolute_error",
        "correlation",
        "snr_db_approx",
        "peak_before",
        "peak_after",
        "peak_delta",
        "rms_before",
        "rms_after",
        "rms_delta",
        "dynamic_range_before_db",
        "dynamic_range_after_db",
        "dynamic_range_delta_db",
        "spectral_centroid_before_hz",
        "spectral_centroid_after_hz",
        "spectral_centroid_delta_hz",
        "spectral_rolloff_before_hz",
        "spectral_rolloff_after_hz",
        "spectral_rolloff_delta_hz",
        "stereo_correlation_before",
        "stereo_correlation_after",
        "stereo_correlation_delta",
        "side_energy_ratio_before",
        "side_energy_ratio_after",
        "side_energy_ratio_delta",
    ):
        assert key in metrics


def test_compare_markdown_includes_metrics_without_unsafe_claims(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    markdown_path = tmp_path / "compare.md"
    _write_sine(reference_path)
    _write_sine(candidate_path, amplitude=0.12)

    write_markdown_report(compare_audio(reference_path, candidate_path), markdown_path)
    text = markdown_path.read_text(encoding="utf-8")

    assert "Comparison Metrics" in text
    assert "`rmse`" in text
    assert "Watermark" not in text
    assert "Fingerprint" not in text
    assert "Detector" not in text
    assert "Provenance" not in text
    assert assert_no_unsafe_public_claims(text) == []
    for forbidden_name in FORBIDDEN_METRIC_NAMES:
        assert forbidden_name not in text


def test_compare_cli_help_works_and_excludes_unsafe_flags(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["compare", "--help"])
    captured = capsys.readouterr()

    assert exc_info.value.code == 0
    assert "fail-on-regression" in captured.out
    for flag in [
        "--aggressive",
        "--extreme",
        "--remove-watermark",
        "--remove-fingerprint",
        "--bypass",
        "--verify-removal",
        "--suno-detector",
    ]:
        assert flag not in captured.out


def test_compare_cli_fail_on_regression_returns_two(tmp_path):
    reference_path = tmp_path / "reference.wav"
    candidate_path = tmp_path / "candidate.wav"
    _write_sine(reference_path, amplitude=0.2)
    sf.write(candidate_path, np.ones(48000, dtype=np.float64), 48000, subtype="FLOAT")

    exit_code = main(
        [
            "compare",
            str(reference_path),
            str(candidate_path),
            "--fail-on-regression",
        ]
    )

    assert exit_code == 2


def test_compare_report_notes_include_safety_boundary(tmp_path):
    input_path = tmp_path / "sine.wav"
    _write_sine(input_path)

    report = compare_audio(input_path, input_path)
    notes = " ".join(report["notes"])

    assert "Compare is read-only" in notes
    assert "does not evaluate or alter watermarks" in notes
    assert "detector signals" in notes


def test_compare_module_does_not_reference_legacy_modules():
    source = (ROOT / "audio_quality_humanizer" / "analysis" / "compare.py").read_text(
        encoding="utf-8"
    )
    forbidden_modules = [
        "ai_audio_fingerprint_remover",
        "aggressive_watermark_remover",
        "sota_watermark_remover",
        "enhanced_suno_detector",
        "optimized_suno_detector",
    ]

    for module in forbidden_modules:
        assert module not in source
