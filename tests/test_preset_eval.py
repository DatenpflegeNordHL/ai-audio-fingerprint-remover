from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf

from audio_quality_humanizer.cli import main
from audio_quality_humanizer.metadata.cleaner import sha256_file
from audio_quality_humanizer.processing.humanize import humanize_audio
from audio_quality_humanizer.reports.markdown_report import write_markdown_report
from audio_quality_humanizer.workflows.doctor import doctor_file
from audio_quality_humanizer.workflows.preset_eval import _recommend, preset_eval


ROOT = Path(__file__).resolve().parents[1]


def _write_sine(path, *, samplerate=48000, duration=1.0, amplitude=0.2):
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate)


def test_preset_eval_basic_writes_outputs_and_keeps_original(tmp_path):
    input_path = tmp_path / "input.wav"
    output_dir = tmp_path / "eval"
    _write_sine(input_path)
    original_hash = sha256_file(input_path)

    report = preset_eval(input_path, output_dir, target="streaming", presets=["subtle", "balanced"])

    assert report["action"] == "preset_eval"
    assert report["target"] == "streaming"
    assert report["input"] == str(input_path)
    assert report["output_dir"] == str(output_dir)
    assert report["presets"] == ["subtle", "balanced"]
    assert "doctor" in report
    assert len(report["results"]) == 2
    assert report["recommended_preset"] in {"subtle", "balanced"}
    assert sha256_file(input_path) == original_hash

    for result in report["results"]:
        assert Path(result["output"]).exists()
        assert Path(result["report"]).exists()
        assert result["humanize_passed"] is True
        assert result["humanize_reverted"] is False
        assert result["compare_passed"] is True
        assert result["error"] is None


def test_preset_eval_invalid_preset_continues(tmp_path):
    input_path = tmp_path / "input.wav"
    output_dir = tmp_path / "eval"
    _write_sine(input_path)

    report = preset_eval(input_path, output_dir, presets=["not-a-preset", "subtle"])

    invalid, valid = report["results"]
    assert invalid["preset"] == "not-a-preset"
    assert invalid["error"]
    assert invalid["blocking_issues"]
    assert Path(invalid["report"]).exists()
    assert not Path(invalid["output"]).exists()
    assert valid["preset"] == "subtle"
    assert Path(valid["output"]).exists()
    assert report["recommended_preset"] == "subtle"


def test_preset_eval_recommendation_skips_failed_and_reverted_results(tmp_path):
    failed_output = tmp_path / "failed.wav"
    reverted_output = tmp_path / "reverted.wav"
    club_output = tmp_path / "club.wav"
    vocal_output = tmp_path / "vocal.wav"
    for path in [failed_output, reverted_output, club_output, vocal_output]:
        path.touch()

    winner = _recommend(
        [
            {
                "preset": "balanced",
                "output": str(failed_output),
                "humanize_passed": False,
                "humanize_reverted": False,
                "compare_passed": True,
                "release_score": 100,
                "compare_score": 100,
                "blocking_issues": [],
                "warnings": [],
            },
            {
                "preset": "subtle",
                "output": str(reverted_output),
                "humanize_passed": True,
                "humanize_reverted": True,
                "compare_passed": True,
                "release_score": 100,
                "compare_score": 100,
                "blocking_issues": [],
                "warnings": [],
            },
            {
                "preset": "club",
                "output": str(club_output),
                "humanize_passed": True,
                "humanize_reverted": False,
                "compare_passed": True,
                "release_score": 90,
                "compare_score": 90,
                "blocking_issues": [],
                "warnings": [],
            },
            {
                "preset": "vocal",
                "output": str(vocal_output),
                "humanize_passed": True,
                "humanize_reverted": False,
                "compare_passed": True,
                "release_score": 90,
                "compare_score": 90,
                "blocking_issues": [],
                "warnings": [],
            },
        ]
    )

    assert winner["preset"] == "vocal"


def test_preset_eval_cli_help_works_and_excludes_unsafe_flags(capsys):
    try:
        main(["preset-eval", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()

    assert "--output-dir" in captured.out
    assert "--fail-if-none" in captured.out
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


def test_preset_eval_cli_fail_if_none_returns_two(tmp_path):
    input_path = tmp_path / "input.wav"
    output_dir = tmp_path / "eval"
    _write_sine(input_path)

    exit_code = main(
        [
            "preset-eval",
            str(input_path),
            "--presets",
            "not-a-preset",
            "--output-dir",
            str(output_dir),
            "--fail-if-none",
        ]
    )

    assert exit_code == 2


def test_preset_eval_markdown_report_can_be_written(tmp_path):
    input_path = tmp_path / "input.wav"
    output_dir = tmp_path / "eval"
    markdown_path = tmp_path / "preset_eval.md"
    _write_sine(input_path)
    report = preset_eval(input_path, output_dir, presets=["subtle"])

    write_markdown_report(report, markdown_path)

    text = markdown_path.read_text(encoding="utf-8")
    assert markdown_path.exists()
    assert "Preset Evaluation Report" in text
    assert "Recommended Preset" in text
    assert "This preset evaluation only compares conservative audio-quality processing outcomes." in text


def test_doctor_and_humanize_markdown_have_polished_summaries(tmp_path):
    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "output.wav"
    doctor_markdown = tmp_path / "doctor.md"
    humanize_markdown = tmp_path / "humanize.md"
    _write_sine(input_path)

    write_markdown_report(doctor_file(input_path), doctor_markdown)
    write_markdown_report(humanize_audio(input_path, output_path), humanize_markdown)

    doctor_text = doctor_markdown.read_text(encoding="utf-8")
    humanize_text = humanize_markdown.read_text(encoding="utf-8")
    assert "## Summary" in doctor_text
    assert "Status" in doctor_text
    assert "Suggested Next Action" in doctor_text
    assert "## Top Recommendations" in doctor_text
    assert "## Summary" in humanize_text
    assert "Safety Result" in humanize_text
    assert "Main Safety Issue" in humanize_text
    assert "Original input was not modified." in humanize_text


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
