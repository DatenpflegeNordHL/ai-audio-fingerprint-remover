from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audio_quality_humanizer.cli import main
from audio_quality_humanizer.metadata.cleaner import sha256_file
from audio_quality_humanizer.reports.markdown_report import write_markdown_report
from audio_quality_humanizer.workflows.batch import batch_run


ROOT = Path(__file__).resolve().parents[1]


def _write_sine(path, *, samplerate=48000, duration=1.0, amplitude=0.2):
    path.parent.mkdir(parents=True, exist_ok=True)
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate)


def _make_two_wavs(input_dir):
    first = input_dir / "a.wav"
    second = input_dir / "b.wav"
    _write_sine(first)
    _write_sine(second)
    return first, second


def test_batch_doctor_mode_processes_two_files(tmp_path):
    input_dir = tmp_path / "tracks"
    output_dir = tmp_path / "reports"
    input_dir.mkdir()
    _make_two_wavs(input_dir)

    report = batch_run(input_dir, output_dir=output_dir, mode="doctor")

    assert report["action"] == "batch"
    assert report["mode"] == "doctor"
    assert report["total_files"] == 2
    assert report["processed_files"] == 2
    assert report["failed_files"] == 0
    assert all(result["report"] for result in report["results"])


def test_batch_analyze_and_release_check_modes_process_two_files(tmp_path):
    input_dir = tmp_path / "tracks"
    input_dir.mkdir()
    _make_two_wavs(input_dir)

    analyze_report = batch_run(input_dir, mode="analyze")
    release_report = batch_run(input_dir, mode="release-check")

    assert analyze_report["processed_files"] == 2
    assert release_report["processed_files"] == 2
    assert release_report["mode"] == "release-check"


def test_batch_humanize_requires_output_dir(tmp_path):
    input_dir = tmp_path / "tracks"
    input_dir.mkdir()
    _make_two_wavs(input_dir)

    with pytest.raises(ValueError, match="requires output_dir"):
        batch_run(input_dir, mode="humanize")


def test_batch_humanize_writes_outputs_and_keeps_originals(tmp_path):
    input_dir = tmp_path / "tracks"
    output_dir = tmp_path / "processed"
    input_dir.mkdir()
    first, second = _make_two_wavs(input_dir)
    before_hashes = {str(path): sha256_file(path) for path in [first, second]}

    report = batch_run(input_dir, output_dir=output_dir, mode="humanize", preset="subtle")

    assert report["processed_files"] == 2
    assert report["failed_files"] == 0
    assert all(result["output"] for result in report["results"])
    assert all(Path(result["output"]).exists() for result in report["results"])
    assert all(Path(result["report"]).exists() for result in report["results"])
    assert sha256_file(first) == before_hashes[str(first)]
    assert sha256_file(second) == before_hashes[str(second)]


def test_batch_fail_fast_stops_after_first_error(tmp_path):
    input_dir = tmp_path / "tracks"
    input_dir.mkdir()
    (input_dir / "a.wav").write_text("not audio", encoding="utf-8")
    _write_sine(input_dir / "b.wav")

    report = batch_run(input_dir, mode="analyze", fail_fast=True)

    assert report["failed_files"] == 1
    assert len(report["results"]) == 1
    assert any("stopped early" in warning for warning in report["warnings"])


def test_batch_no_matching_files_returns_warning(tmp_path):
    input_dir = tmp_path / "tracks"
    input_dir.mkdir()

    report = batch_run(input_dir, pattern="*.wav")

    assert report["total_files"] == 0
    assert report["warnings"]


def test_batch_recursive_finds_nested_files(tmp_path):
    input_dir = tmp_path / "tracks"
    nested = input_dir / "nested"
    _write_sine(nested / "inside.wav")

    report = batch_run(input_dir, mode="doctor", recursive=True)

    assert report["total_files"] == 1
    assert report["processed_files"] == 1


def test_batch_cli_help_works_and_excludes_unsafe_flags(capsys):
    try:
        main(["batch", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()

    assert "--fail-on-error" in captured.out
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


def test_workflows_package_does_not_reference_legacy_modules():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "audio_quality_humanizer" / "workflows").glob("*.py")
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


def test_batch_markdown_report_can_be_written(tmp_path):
    input_dir = tmp_path / "tracks"
    markdown_path = tmp_path / "batch.md"
    input_dir.mkdir()
    _make_two_wavs(input_dir)
    report = batch_run(input_dir, mode="doctor")

    write_markdown_report(report, markdown_path)

    assert markdown_path.exists()
    assert "Batch Workflow Report" in markdown_path.read_text(encoding="utf-8")
