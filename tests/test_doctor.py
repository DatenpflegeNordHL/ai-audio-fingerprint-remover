from __future__ import annotations

import numpy as np
import soundfile as sf

from audio_quality_humanizer.cli import main
from audio_quality_humanizer.reports.markdown_report import write_markdown_report
from audio_quality_humanizer.workflows.doctor import doctor_file


def _write_sine(path, *, samplerate=48000, duration=1.0, amplitude=0.2):
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate)


def test_doctor_file_returns_combined_report(tmp_path):
    input_path = tmp_path / "input.wav"
    _write_sine(input_path)

    report = doctor_file(input_path, target="streaming")

    assert report["action"] == "doctor"
    assert "metadata" in report
    assert "provenance" in report
    assert "analysis" in report
    assert "release_check" in report
    assert isinstance(report["passed"], bool)
    assert isinstance(report["score"], int)
    notes = " ".join(report["notes"])
    assert "Doctor is read-only" in notes
    assert "does not evaluate or alter watermarks" in notes


def test_doctor_cli_help_works_and_excludes_unsafe_flags(capsys):
    try:
        main(["doctor", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()

    assert "--fail-on-issue" in captured.out
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


def test_doctor_markdown_report_can_be_written(tmp_path):
    input_path = tmp_path / "input.wav"
    markdown_path = tmp_path / "doctor.md"
    _write_sine(input_path)
    report = doctor_file(input_path, target="streaming")

    write_markdown_report(report, markdown_path)

    assert markdown_path.exists()
    assert "Doctor Preflight" in markdown_path.read_text(encoding="utf-8")
