from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audio_quality_humanizer.analysis.compare import compare_audio
from audio_quality_humanizer.cli import main


ROOT = Path(__file__).resolve().parents[1]


def _write_sine(path, *, amplitude=0.2, samplerate=48000, duration=1.0):
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate)


def test_compare_identical_file_passes_with_tiny_difference(tmp_path):
    input_path = tmp_path / "sine.wav"
    _write_sine(input_path)

    report = compare_audio(input_path, input_path)

    assert report["passed"] is True
    assert report["score"] >= 95
    assert report["waveform_similarity"]["likely_identical_audio"] is True
    assert report["waveform_similarity"]["rms_difference"] == 0.0


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
