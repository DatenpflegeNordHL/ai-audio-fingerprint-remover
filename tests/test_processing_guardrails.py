from __future__ import annotations

import json

import numpy as np

from audio_quality_humanizer.processing.guardrails import (
    calculate_signal_guardrail_report,
    sanitize_audio_array,
    validate_audio_array,
    validate_processing_result,
    validate_samplerate,
)


def test_validate_audio_array_accepts_normal_sine_wave():
    samplerate = 48000
    t = np.linspace(0.0, 0.1, int(samplerate * 0.1), endpoint=False)
    audio = 0.25 * np.sin(2.0 * np.pi * 440.0 * t)

    report = validate_audio_array(audio)

    assert report["valid"] is True
    assert report["numeric"] is True
    assert report["nan_count"] == 0
    assert report["inf_count"] == 0
    assert report["shape"] == [4800]
    assert report["channel_count"] == 1


def test_validate_audio_array_reports_silent_mono_and_stereo_shapes():
    mono = np.zeros(12, dtype=np.float64)
    stereo = np.zeros((12, 2), dtype=np.float64)

    mono_report = validate_audio_array(mono)
    stereo_report = validate_audio_array(stereo)

    assert mono_report["valid"] is True
    assert mono_report["silent"] is True
    assert mono_report["channel_count"] == 1
    assert stereo_report["valid"] is True
    assert stereo_report["silent"] is True
    assert stereo_report["shape"] == [12, 2]
    assert stereo_report["channel_count"] == 2


def test_validate_audio_array_detects_empty_nan_inf_and_non_numeric_values():
    assert validate_audio_array(np.array([]))["valid"] is False

    problem_audio = np.array([0.1, np.nan, np.inf, -np.inf])
    problem_report = validate_audio_array(problem_audio)
    assert problem_report["valid"] is False
    assert problem_report["nan_count"] == 1
    assert problem_report["inf_count"] == 2

    non_numeric_report = validate_audio_array(np.array(["left", "right"]))
    assert non_numeric_report["valid"] is False
    assert non_numeric_report["numeric"] is False


def test_validate_audio_array_warns_when_peak_reaches_full_scale():
    report = validate_audio_array(np.array([0.0, 1.0], dtype=np.float64))

    assert report["valid"] is True
    assert report["peak"] == 1.0
    assert report["peak_at_or_above_full_scale"] is True
    assert report["peak_above_full_scale"] is False
    assert "Peak level reaches full scale." in report["warnings"]


def test_signal_guardrail_report_warns_when_input_peak_reaches_full_scale():
    report = calculate_signal_guardrail_report(np.array([0.0, -1.0], dtype=np.float64), samplerate=48000)
    guardrails = report["guardrails"]

    assert guardrails["input_valid"] is True
    assert guardrails["peak_before"] == 1.0
    assert "Peak level reaches full scale." in guardrails["warnings"]


def test_sanitize_audio_array_replaces_only_nonfinite_values_without_normalizing():
    audio = np.array([0.5, np.nan, np.inf, -np.inf], dtype=np.float64)

    sanitized, report = sanitize_audio_array(audio)

    assert report["changed"] is True
    assert report["nan_count_before"] == 1
    assert report["inf_count_before"] == 2
    assert report["nan_count_after"] == 0
    assert report["inf_count_after"] == 0
    assert sanitized.tolist() == [0.5, 0.0, 0.0, 0.0]
    assert float(np.max(np.abs(sanitized))) == 0.5


def test_validate_samplerate_detects_invalid_values():
    assert validate_samplerate(48000)["valid"] is True
    assert validate_samplerate(0)["valid"] is False
    assert validate_samplerate(-1)["valid"] is False
    assert validate_samplerate(4000)["valid"] is False
    assert validate_samplerate("48000")["valid"] is False


def test_validate_processing_result_detects_shape_length_and_peak_problems():
    before = np.zeros((8, 2), dtype=np.float64)
    shape_mismatch = np.zeros((8, 1), dtype=np.float64)
    length_mismatch = np.zeros((10, 2), dtype=np.float64)
    hot_output = np.full((8, 2), 1.2, dtype=np.float64)

    assert validate_processing_result(before, before)["valid"] is True

    shape_report = validate_processing_result(before, shape_mismatch)
    assert shape_report["valid"] is False
    assert shape_report["shape_changed"] is True
    assert shape_report["channel_count_changed"] is True

    length_report = validate_processing_result(before, length_mismatch)
    assert length_report["valid"] is False
    assert length_report["length_changed"] is True

    peak_report = validate_processing_result(before, hot_output, max_peak_allowed=1.0)
    assert peak_report["valid"] is False
    assert peak_report["peak_above_allowed"] is True


def test_calculate_signal_guardrail_report_is_json_safe_and_stable():
    before = np.zeros((4, 1), dtype=np.float64)
    after = before.copy()

    report = calculate_signal_guardrail_report(before, after, samplerate=48000)
    guardrails = report["guardrails"]

    assert guardrails["input_valid"] is True
    assert guardrails["output_valid"] is True
    assert guardrails["shape_before"] == [4, 1]
    assert guardrails["shape_after"] == [4, 1]
    assert guardrails["samplerate_valid"] is True
    json.dumps(report)


def test_very_short_audio_is_valid_when_numeric_and_finite():
    report = validate_audio_array(np.array([0.0], dtype=np.float64))

    assert report["valid"] is True
    assert report["frame_count"] == 1
