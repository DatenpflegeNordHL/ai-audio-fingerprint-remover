from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SAFETY = ROOT / "SAFETY.md"
GITIGNORE = ROOT / ".gitignore"
FORBIDDEN_METRIC_NAMES = (
    "watermark_score",
    "fingerprint_score",
    "detector_score",
    "evasion_score",
    "bypass_score",
    "recognition_score",
    "provenance_score",
    "detectability_score",
    "origin_score",
    "source_attribution_score",
)


def test_readme_documents_compare_metrics_example_and_boundaries():
    text = README.read_text(encoding="utf-8")

    assert "comparison_metrics" in text
    assert "ai-humanizer compare before.wav after.wav" in text
    assert "--target club" in text
    assert "--report compare.json" in text
    assert "--markdown compare.md" in text
    assert "read-only before/after quality deltas" in text
    assert "reported as `null`" in text
    assert "JSON outputs are safe to serialize" in text
    assert "do not certify distributor or platform acceptance" in text
    assert "do not evaluate attribution, recognition, provenance, watermark, fingerprint, detector behavior" in text


def test_safety_blocks_unsafe_compare_metric_names():
    text = SAFETY.read_text(encoding="utf-8")

    assert "Compare metrics must use neutral audio-quality names only." in text
    assert "Compare metrics must not use unsafe score names" in text
    for forbidden_name in FORBIDDEN_METRIC_NAMES:
        assert forbidden_name not in text


def test_v011_validation_outputs_are_ignored():
    text = GITIGNORE.read_text(encoding="utf-8")

    assert "v011_validation_outputs/" in text
