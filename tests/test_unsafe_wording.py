from __future__ import annotations

import contextlib
import io
from pathlib import Path

import pytest

from audio_quality_humanizer.cli import _build_parser
from audio_quality_humanizer.safety import assert_no_unsafe_public_claims


ROOT = Path(__file__).resolve().parents[1]


def test_readme_has_no_unsafe_feature_claims():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert assert_no_unsafe_public_claims(readme) == []


def test_safety_document_exists():
    assert (ROOT / "SAFETY.md").exists()


def test_cli_help_excludes_unsafe_flags():
    parser = _build_parser()
    help_parts = [parser.format_help()]
    for command in ["analyze", "release-check", "compare", "humanize", "inspect-metadata", "clean-metadata"]:
        stdout = io.StringIO()
        with pytest.raises(SystemExit), contextlib.redirect_stdout(stdout):
            parser.parse_args([command, "--help"])
        help_parts.append(stdout.getvalue())
    help_text = "\n".join(help_parts)

    forbidden_flags = [
        "--aggressive",
        "--extreme",
        "--remove-watermark",
        "--remove-fingerprint",
        "--bypass",
        "--verify-removal",
        "--suno-detector",
    ]

    for flag in forbidden_flags:
        assert flag not in help_text


def test_safety_checker_catches_unsafe_sample_phrases():
    text = """
    This imaginary tool offers watermark removal, detector bypass, bypass detectors,
    evade detection mode, neutralize watermark, verify removal,
    watermarks detected and removed, spectral watermark detection,
    and watermark elimination.
    """

    matches = assert_no_unsafe_public_claims(text)

    assert "watermark removal" in matches
    assert "detector bypass" in matches
    assert "bypass detectors" in matches
    assert "evade detection" in matches
    assert "neutralize watermark" in matches
    assert "verify removal" in matches
    assert "watermarks detected and removed" in matches
    assert "spectral watermark detection" in matches
    assert "watermark elimination" in matches


def test_analysis_package_does_not_reference_legacy_modules():
    analysis_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "audio_quality_humanizer" / "analysis").glob("*.py")
    )
    forbidden_modules = [
        "ai_audio_fingerprint_remover",
        "aggressive_watermark_remover",
        "sota_watermark_remover",
        "enhanced_suno_detector",
        "optimized_suno_detector",
    ]

    for module in forbidden_modules:
        assert module not in analysis_source


def test_processing_package_does_not_reference_legacy_modules():
    processing_source = "\n".join(
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
        assert module not in processing_source
