from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.cli import main
from audio_quality_humanizer.metadata.cleaner import sha256_file
from audio_quality_humanizer.processing.humanize import humanize_audio
from audio_quality_humanizer.reports.markdown_report import write_markdown_report


ROOT = Path(__file__).resolve().parents[1]


def _write_sine(path, *, amplitude=0.2, samplerate=48000, duration=1.0, subtype=None):
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate, subtype=subtype)


def test_humanize_subtle_preserves_input_and_reports(tmp_path):
    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "output.wav"
    _write_sine(input_path, amplitude=0.2)
    before_hash = sha256_file(input_path)

    report = humanize_audio(input_path, output_path, preset="subtle", target="streaming")

    assert input_path.exists()
    assert output_path.exists()
    assert sha256_file(input_path) == before_hash
    assert report["passed"] is True
    assert report["reverted"] is False
    assert "before_analysis" in report
    assert "after_analysis" in report
    assert "comparison" in report
    assert "safety" in report
    assert report["before_analysis"]["samplerate"] == report["after_analysis"]["samplerate"]
    assert report["before_analysis"]["channels"] == report["after_analysis"]["channels"]
    assert abs(report["comparison"]["compatibility"]["duration_delta_ms"]) <= 10.0


def test_humanize_peak_ceiling_prevents_clipping(tmp_path):
    input_path = tmp_path / "hot.wav"
    output_path = tmp_path / "hot_out.wav"
    _write_sine(input_path, amplitude=0.99, subtype="FLOAT")

    report = humanize_audio(input_path, output_path, preset="balanced", target="streaming")
    output_analysis = analyze_audio(output_path)

    assert report["passed"] is True
    assert output_analysis["clipping_sample_count"] == 0
    assert output_analysis["peak_dbfs"] <= -0.9


def test_afro_club_low_end_mono_preserves_shape_without_introducing_warning(tmp_path):
    input_path = tmp_path / "afro.wav"
    output_path = tmp_path / "afro_out.wav"
    samplerate = 48000
    t = np.linspace(0.0, 1.0, samplerate, endpoint=False)
    mid = 0.30 * np.sin(2.0 * np.pi * 60.0 * t)
    side = 0.10 * np.sin(2.0 * np.pi * 60.0 * t)
    left = mid + side
    right = mid - side
    sf.write(input_path, np.column_stack([left, right]), samplerate, subtype="FLOAT")

    report = humanize_audio(input_path, output_path, preset="afro-club", target="club")

    assert output_path.exists()
    assert report["after_analysis"]["channels"] == 2
    assert report["after_analysis"]["frames"] == report["before_analysis"]["frames"]
    assert not (
        report["after_analysis"]["low_end_stereo_warning"]
        and not report["before_analysis"]["low_end_stereo_warning"]
    )


def test_humanize_cli_help_works_and_excludes_unsafe_flags(capsys):
    try:
        main(["humanize", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()

    assert "--preset" in captured.out
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


def test_processing_package_does_not_reference_legacy_modules():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "audio_quality_humanizer" / "processing").glob("*.py")
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


def test_humanize_markdown_report_can_be_written(tmp_path):
    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "output.wav"
    markdown_path = tmp_path / "humanize.md"
    _write_sine(input_path, amplitude=0.2)
    report = humanize_audio(input_path, output_path, preset="subtle", target="streaming")

    write_markdown_report(report, markdown_path)

    assert markdown_path.exists()
    assert "Conservative Humanize Report" in markdown_path.read_text(encoding="utf-8")
