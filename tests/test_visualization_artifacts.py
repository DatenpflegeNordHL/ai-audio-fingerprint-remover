from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf

from audio_quality_humanizer.cli import main
from audio_quality_humanizer.safety import assert_no_unsafe_public_claims
from audio_quality_humanizer.visualization_artifacts import (
    ALLOWED_TOOLTIP_LABELS,
    build_visualization_artifacts,
    build_visualization_comparison,
)


FORBIDDEN_LABELS = (
    "fingerprint removed",
    "watermark removed",
    "AI trace removed",
    "detector bypassed",
    "undetectable",
    "hidden identifier removed",
    "provenance removed",
    "source attribution removed",
    "C2PA removed",
    "origin removed",
    "detectability reduced",
    "platform certified",
    "distributor accepted",
)


def _write_sine(
    path: Path,
    *,
    amplitude: float = 0.2,
    samplerate: int = 48000,
    duration: float = 1.0,
    frequency: float = 440.0,
    stereo: bool = False,
) -> None:
    t = np.linspace(0.0, duration, max(1, int(samplerate * duration)), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * frequency * t)
    if stereo:
        audio = np.column_stack([audio, audio * 0.8])
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


def _assert_json_safe(report: dict) -> None:
    encoded = json.dumps(report, allow_nan=False)
    for value in _walk_values(report):
        if isinstance(value, float):
            assert math.isfinite(value)
    for label in FORBIDDEN_LABELS:
        assert label.casefold() not in encoded.casefold()


def test_visualization_report_contains_expected_top_level_keys(tmp_path):
    input_path = tmp_path / "input.wav"
    _write_sine(input_path)

    report = build_visualization_artifacts(input_path, max_time_bins=32, max_frequency_bins=24)

    assert report["action"] == "visualize"
    assert report["schema_version"] == "1.0"
    assert {"source", "waveform_peaks", "spectrogram", "metric_cards", "tooltip_regions", "safety_notes"} <= set(report)
    assert report["source"]["sample_rate"] == 48000
    _assert_json_safe(report)


def test_waveform_peaks_and_spectrogram_are_bounded(tmp_path):
    input_path = tmp_path / "input.wav"
    _write_sine(input_path, duration=2.0)

    report = build_visualization_artifacts(input_path, max_time_bins=16, max_frequency_bins=12, max_waveform_windows=20)

    assert 0 < report["waveform_peaks"]["window_count"] <= 20
    assert len(report["waveform_peaks"]["peaks"]) == report["waveform_peaks"]["window_count"]
    assert len(report["spectrogram"]["time_bins"]) <= 16
    assert len(report["spectrogram"]["frequency_bins_hz"]) <= 12
    assert len(report["spectrogram"]["energy_db"]) <= 16
    assert len(report["spectrogram"]["energy_db"][0]) <= 12


def test_metric_cards_exist_for_single_file(tmp_path):
    input_path = tmp_path / "input.wav"
    _write_sine(input_path)

    cards = build_visualization_artifacts(input_path)["metric_cards"]

    for key in (
        "peak_dbfs",
        "rms_dbfs",
        "clipping_sample_count",
        "spectral_centroid_hz",
        "spectral_rolloff_95_hz",
        "duration_seconds",
        "sample_rate",
        "channel_count",
    ):
        assert key in cards


def test_silent_short_mono_and_stereo_audio_are_json_safe(tmp_path):
    silent = tmp_path / "silent.wav"
    short = tmp_path / "short.wav"
    mono = tmp_path / "mono.wav"
    stereo = tmp_path / "stereo.wav"
    sf.write(silent, np.zeros(4800), 48000)
    sf.write(short, np.asarray([0.0, 0.1, -0.1]), 48000)
    _write_sine(mono)
    _write_sine(stereo, stereo=True)

    for path in (silent, short, mono, stereo):
        report = build_visualization_artifacts(path, max_time_bins=8, max_frequency_bins=8)
        _assert_json_safe(report)
        assert report["spectrogram"]["summary"]["time_bin_count"] >= 1


def test_visualize_compare_contains_difference_map_and_json_safe_values(tmp_path):
    reference = tmp_path / "reference.wav"
    candidate = tmp_path / "candidate.wav"
    _write_sine(reference)
    _write_sine(candidate, amplitude=0.1)

    report = build_visualization_comparison(reference, candidate, max_time_bins=16, max_frequency_bins=16)

    assert report["action"] == "visualize-compare"
    assert report["difference_map"]["summary"]["comparison_available"] is True
    assert report["comparison_metrics"]["rmse"] > 0.0
    _assert_json_safe(report)


def test_visualize_compare_identical_input_has_near_zero_difference(tmp_path):
    input_path = tmp_path / "input.wav"
    _write_sine(input_path)

    report = build_visualization_comparison(input_path, input_path, max_time_bins=16, max_frequency_bins=16)
    summary = report["difference_map"]["summary"]

    assert summary["comparison_available"] is True
    assert summary["mean_abs_delta_db"] == 0.0
    assert summary["max_abs_delta_db"] == 0.0
    assert summary["changed_bin_count"] == 0
    assert summary["changed_bin_ratio"] == 0.0


def test_visualize_compare_gain_change_has_nonzero_difference(tmp_path):
    reference = tmp_path / "reference.wav"
    candidate = tmp_path / "candidate.wav"
    _write_sine(reference, amplitude=0.2)
    _write_sine(candidate, amplitude=0.05)

    summary = build_visualization_comparison(reference, candidate, max_time_bins=16, max_frequency_bins=16)["difference_map"]["summary"]

    assert summary["mean_abs_delta_db"] > 0.0
    assert summary["max_abs_delta_db"] > 0.0
    assert summary["changed_bin_count"] > 0


def test_visualize_compare_different_tones_have_spectral_difference(tmp_path):
    reference = tmp_path / "reference.wav"
    candidate = tmp_path / "candidate.wav"
    _write_sine(reference, frequency=220.0)
    _write_sine(candidate, frequency=2200.0)

    report = build_visualization_comparison(reference, candidate, max_time_bins=16, max_frequency_bins=32)

    assert report["difference_map"]["summary"]["mean_abs_delta_db"] > 0.0
    assert abs(report["comparison_metrics"]["spectral_centroid_delta_hz"]) > 500.0


def test_visualize_compare_tooltip_regions_use_allowed_labels_only(tmp_path):
    reference = tmp_path / "reference.wav"
    candidate = tmp_path / "candidate.wav"
    _write_sine(reference, amplitude=0.2, frequency=220.0)
    _write_sine(candidate, amplitude=0.05, frequency=2200.0)

    report = build_visualization_comparison(reference, candidate, max_time_bins=16, max_frequency_bins=32)
    labels = {region["label"] for region in report["tooltip_regions"]}

    assert labels
    assert labels <= ALLOWED_TOOLTIP_LABELS
    encoded = json.dumps(report, allow_nan=False)
    for forbidden in FORBIDDEN_LABELS:
        assert forbidden.casefold() not in encoded.casefold()


def test_visualize_compare_samplerate_mismatch_is_safely_reported(tmp_path):
    reference = tmp_path / "reference.wav"
    candidate = tmp_path / "candidate.wav"
    _write_sine(reference, samplerate=44100)
    _write_sine(candidate, samplerate=48000)

    report = build_visualization_comparison(reference, candidate)
    summary = report["difference_map"]["summary"]

    assert report["compatibility"]["samplerate_match"] is False
    assert summary["comparison_available"] is False
    assert summary["reason"] == "sample_rate_mismatch"
    assert summary["mean_abs_delta_db"] is None
    _assert_json_safe(report)


def test_visualize_cli_writes_report_json_for_synthetic_audio(tmp_path):
    input_path = tmp_path / "input.wav"
    report_path = tmp_path / "visualization.json"
    _write_sine(input_path)

    assert main(["visualize", str(input_path), "--report", str(report_path)]) == 0

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["action"] == "visualize"
    _assert_json_safe(report)


def test_visualize_compare_cli_writes_report_json_for_synthetic_audio(tmp_path):
    reference = tmp_path / "reference.wav"
    candidate = tmp_path / "candidate.wav"
    report_path = tmp_path / "visual_compare.json"
    _write_sine(reference)
    _write_sine(candidate, amplitude=0.1)

    assert main(["visualize-compare", str(reference), str(candidate), "--report", str(report_path)]) == 0

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["action"] == "visualize-compare"
    _assert_json_safe(report)


def test_visualize_cli_help_is_safe(capsys):
    for command in ("visualize", "visualize-compare"):
        try:
            main([command, "--help"])
        except SystemExit as exc:
            assert exc.code == 0
        output = capsys.readouterr().out
        assert assert_no_unsafe_public_claims(output) == []
