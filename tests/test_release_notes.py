from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_NOTES = ROOT / "docs" / "releases" / "V0_10_0_RELEASE_NOTES.md"
V0_11_RELEASE_NOTES = ROOT / "docs" / "releases" / "V0_11_0_RELEASE_NOTES.md"
V0_12_RELEASE_NOTES = ROOT / "docs" / "releases" / "V0_12_0_RELEASE_NOTES.md"
README = ROOT / "README.md"
GITIGNORE = ROOT / ".gitignore"


def test_v0_10_release_notes_exist_and_name_tag():
    text = RELEASE_NOTES.read_text(encoding="utf-8")

    assert RELEASE_NOTES.exists()
    assert "v0.10.0" in text
    assert "Tag: `v0.10.0`" in text


def test_v0_10_release_notes_keep_project_reborn_reference_only():
    text = RELEASE_NOTES.read_text(encoding="utf-8")

    assert "Project Reborn reference-only" in text
    assert "Project Reborn was not imported, executed, packaged, or exposed" in text


def test_v0_10_release_notes_do_not_include_local_paths_or_certification_claims():
    text = RELEASE_NOTES.read_text(encoding="utf-8")

    assert "/Users/" not in text
    assert "official platform certification" not in text.casefold()


def test_readme_references_guardrail_reports_and_release_notes():
    text = README.read_text(encoding="utf-8")

    assert "v0.10.0 guardrail reports" in text
    assert "Signal Guardrails" in text
    assert "docs/releases/V0_10_0_RELEASE_NOTES.md" in text
    assert "docs/releases/V0_11_0_RELEASE_NOTES.md" in text
    assert "docs/releases/V0_12_0_RELEASE_NOTES.md" in text


def test_gitignore_ignores_local_v0_10_validation_outputs():
    text = GITIGNORE.read_text(encoding="utf-8")

    assert "v010_validation_outputs/" in text


def test_v0_11_release_notes_exist_and_describe_compare_metrics():
    text = V0_11_RELEASE_NOTES.read_text(encoding="utf-8")

    assert V0_11_RELEASE_NOTES.exists()
    assert "v0.11.0" in text
    assert "comparison_metrics" in text
    assert "read-only" in text
    assert "No new CLI command was added." in text
    assert "No generated validation outputs are committed." in text


def test_v0_11_release_notes_keep_safe_boundaries():
    text = V0_11_RELEASE_NOTES.read_text(encoding="utf-8")
    lowered = text.casefold()

    assert "/Users/" not in text
    assert "platform certification" not in lowered
    assert "platform-certification claims" in lowered
    assert "Project Reborn source was not copied, imported, executed, packaged, or exposed." in text
    assert "not mastering certification" in lowered


def test_v0_12_release_notes_exist_and_describe_visualization_artifacts():
    text = V0_12_RELEASE_NOTES.read_text(encoding="utf-8")

    assert V0_12_RELEASE_NOTES.exists()
    assert "v0.12.0" in text
    assert "Tag: `v0.12.0`" in text
    assert "ai-humanizer visualize input.wav" in text
    assert "ai-humanizer visualize-compare before.wav after.wav" in text
    assert "schema_version" in text
    assert "waveform_peaks" in text
    assert "spectrogram" in text
    assert "difference_map" in text
    assert "Generated validation reports remained ignored and uncommitted." in text


def test_v0_12_release_notes_keep_safe_boundaries():
    text = V0_12_RELEASE_NOTES.read_text(encoding="utf-8")
    lowered = text.casefold()

    assert "/Users/" not in text
    assert "not mastering certification" in lowered
    assert "do not predict platform or distributor acceptance" in lowered
    assert "do not evaluate or remove watermarks, fingerprints, provenance" in lowered
    assert "Project Reborn source was not copied, imported, executed, packaged, or exposed." in text
