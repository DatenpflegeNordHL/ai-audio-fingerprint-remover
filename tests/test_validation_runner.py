from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf

from audio_quality_humanizer.cli import main
from audio_quality_humanizer.metadata.cleaner import sha256_file
from audio_quality_humanizer.reports.markdown_report import write_markdown_report
from audio_quality_humanizer.validation.runner import run_validation


ROOT = Path(__file__).resolve().parents[1]


def _write_sine(path, *, samplerate=48000, duration=1.0, amplitude=0.2):
    t = np.linspace(0.0, duration, int(samplerate * duration), endpoint=False)
    audio = amplitude * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate)


def _write_manifest(path: Path, sample_path: Path) -> None:
    manifest = {
        "project": "Local validation test",
        "target": "streaming",
        "samples": [
            {
                "id": "sample_01",
                "path": str(sample_path.relative_to(path.parent)),
                "target": "streaming",
                "presets": ["subtle", "balanced"],
                "notes": "Temporary test sample",
            }
        ],
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def test_run_validation_processes_sample_and_keeps_original(tmp_path):
    sample_path = tmp_path / "samples" / "sample.wav"
    manifest_path = tmp_path / "validation_manifest.json"
    output_dir = tmp_path / "validation_outputs"
    sample_path.parent.mkdir()
    _write_sine(sample_path)
    _write_manifest(manifest_path, sample_path)
    original_hash = sha256_file(sample_path)

    report = run_validation(manifest_path, output_dir, default_target="streaming")

    assert report["action"] == "validate_samples"
    assert report["processed_samples"] == 1
    assert report["failed_samples"] == 0
    assert len(report["results"]) == 1
    result = report["results"][0]
    assert result["id"] == "sample_01"
    assert result["recommended_preset"] in {"subtle", "balanced", None}
    assert result["original_unchanged"] is True
    assert Path(result["report"]).exists()
    assert output_dir.exists()
    assert sha256_file(sample_path) == original_hash


def test_validate_samples_cli_help_works_and_excludes_unsafe_flags(capsys):
    try:
        main(["validate-samples", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    captured = capsys.readouterr()

    assert "--output-dir" in captured.out
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


def test_validate_samples_cli_fail_on_error_returns_two(tmp_path):
    manifest_path = tmp_path / "validation_manifest.json"
    manifest_path.write_text(
        json.dumps({"samples": [{"id": "missing", "path": "missing.wav"}]}) + "\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "validate-samples",
            str(manifest_path),
            "--output-dir",
            str(tmp_path / "validation_outputs"),
            "--fail-on-error",
        ]
    )

    assert exit_code == 2


def test_validation_markdown_report_can_be_written(tmp_path):
    sample_path = tmp_path / "samples" / "sample.wav"
    manifest_path = tmp_path / "validation_manifest.json"
    output_dir = tmp_path / "validation_outputs"
    markdown_path = tmp_path / "validation.md"
    sample_path.parent.mkdir()
    _write_sine(sample_path)
    _write_manifest(manifest_path, sample_path)
    report = run_validation(manifest_path, output_dir, default_target="streaming")

    write_markdown_report(report, markdown_path)

    text = markdown_path.read_text(encoding="utf-8")
    assert markdown_path.exists()
    assert "Real-World Sample Validation Report" in text
    assert "Recommended Preset Counts" in text
    assert "This validation workflow only evaluates local user-supplied audio-quality" in text


def test_validation_package_does_not_reference_legacy_modules():
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "audio_quality_humanizer" / "validation").glob("*.py")
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
