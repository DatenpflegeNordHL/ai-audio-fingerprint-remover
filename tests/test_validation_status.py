from __future__ import annotations

import builtins
import json
from pathlib import Path

from audio_quality_humanizer.cli import main
from audio_quality_humanizer.reports.markdown_report import write_markdown_report
from audio_quality_humanizer.validation.status import _looks_like_project_root, validation_status


ROOT = Path(__file__).resolve().parents[1]


def test_validation_status_project_root_detection(tmp_path):
    assert _looks_like_project_root(tmp_path) is False

    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Test\n", encoding="utf-8")
    (tmp_path / "audio_quality_humanizer").mkdir()

    assert _looks_like_project_root(tmp_path) is True


def test_validation_status_missing_files_reports_warnings_and_suggestions(tmp_path):
    report = validation_status(tmp_path)

    assert report["action"] == "validation_status"
    assert report["looks_like_project_root"] is False
    assert "validation_manifest.json was not found under the inspected root." in report["warnings"]
    assert "validation.md and validation.json were not found under the inspected root." in report["warnings"]
    assert 'python3 -m pip install -e ".[test]"' in report["suggested_commands"]
    assert "cp examples/validation_manifest.example.json validation_manifest.json" in report["suggested_commands"]


def test_validation_status_find_reports(tmp_path):
    paths = [
        tmp_path / "validation.md",
        tmp_path / "validation.json",
        tmp_path / "nested" / "sample.validation.json",
        tmp_path / "nested" / "sample.eval.json",
        tmp_path / "nested" / "preset_eval.json",
        tmp_path / "nested" / "preset_eval.md",
    ]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}", encoding="utf-8")

    report = validation_status(tmp_path, find=True)

    found = set(report["found_reports"])
    for path in paths:
        assert str(path.resolve()) in found


def test_validation_status_markdown_report_can_be_written(tmp_path):
    report = validation_status(tmp_path)
    markdown_path = tmp_path / "validation_status.md"

    write_markdown_report(report, markdown_path)

    text = markdown_path.read_text(encoding="utf-8")
    assert markdown_path.exists()
    assert "Validation Status Report" in text
    assert "Suggested Commands" in text
    assert "This status command only inspects local file paths" in text


def test_validation_status_cli_help_works(capsys):
    try:
        main(["validation-status", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()

    assert "--root" in captured.out
    assert "--find" in captured.out
    assert "--max-depth" in captured.out


def test_validation_status_cli_runs_from_arbitrary_temp_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    json_path = tmp_path / "validation_status.json"
    markdown_path = tmp_path / "validation_status.md"

    exit_code = main(
        [
            "validation-status",
            "--root",
            str(tmp_path),
            "--find",
            "--json",
            str(json_path),
            "--markdown",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    assert json_path.exists()
    assert markdown_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["action"] == "validation_status"
    assert data["root"] == str(tmp_path.resolve())


def test_validation_status_does_not_open_or_process_audio_files(tmp_path, monkeypatch):
    audio_path = tmp_path / "validation_samples" / "sample.wav"
    audio_path.parent.mkdir()
    audio_path.write_bytes(b"not real audio")
    original_open = builtins.open

    def guarded_open(file, *args, **kwargs):
        if Path(file) == audio_path:
            raise AssertionError("validation-status must not open audio files")
        return original_open(file, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", guarded_open)

    report = validation_status(tmp_path, find=True)

    assert report["action"] == "validation_status"


def test_validation_status_help_excludes_unsafe_flags(capsys):
    try:
        main(["validation-status", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()

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


def test_validation_status_does_not_reference_legacy_modules():
    source = (ROOT / "audio_quality_humanizer" / "validation" / "status.py").read_text(encoding="utf-8")
    forbidden_modules = [
        "ai_audio_fingerprint_remover",
        "aggressive_watermark_remover",
        "sota_watermark_remover",
        "enhanced_suno_detector",
        "optimized_suno_detector",
        "watermark_effectiveness_tester",
        "advanced_watermark_analysis",
        "advanced_steganography_detector",
        "neural_watermark_detector",
        "next_gen_remover",
    ]

    for module in forbidden_modules:
        assert module not in source
