from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_NOTES = ROOT / "docs" / "releases" / "V0_10_0_RELEASE_NOTES.md"
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


def test_gitignore_ignores_local_v0_10_validation_outputs():
    text = GITIGNORE.read_text(encoding="utf-8")

    assert "v010_validation_outputs/" in text
