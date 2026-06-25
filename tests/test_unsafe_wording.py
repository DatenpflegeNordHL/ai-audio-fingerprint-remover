from __future__ import annotations

from pathlib import Path

from audio_quality_humanizer.cli import _build_parser
from audio_quality_humanizer.safety import assert_no_unsafe_public_claims


ROOT = Path(__file__).resolve().parents[1]


def test_readme_has_no_unsafe_feature_claims():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert assert_no_unsafe_public_claims(readme) == []


def test_safety_document_exists():
    assert (ROOT / "SAFETY.md").exists()


def test_cli_help_excludes_unsafe_flags():
    help_text = _build_parser().format_help()
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
    This imaginary tool offers watermark removal, detector bypass,
    evade detection mode, neutralize watermark, verify removal,
    watermarks detected and removed, spectral watermark detection,
    and watermark elimination.
    """

    matches = assert_no_unsafe_public_claims(text)

    assert "watermark removal" in matches
    assert "detector bypass" in matches
    assert "evade detection" in matches
    assert "neutralize watermark" in matches
    assert "verify removal" in matches
    assert "watermarks detected and removed" in matches
    assert "spectral watermark detection" in matches
    assert "watermark elimination" in matches
