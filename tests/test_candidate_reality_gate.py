from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE_MARKDOWN = ROOT / "docs" / "design" / "CANDIDATE_REALITY_GATE.md"
GATE_JSON = ROOT / "docs" / "design" / "candidate_reality_gate.json"
README = ROOT / "README.md"
SAFETY = ROOT / "SAFETY.md"
GITIGNORE = ROOT / ".gitignore"


def _gate() -> dict:
    return json.loads(GATE_JSON.read_text(encoding="utf-8"))


def test_candidate_reality_gate_files_exist():
    assert GATE_MARKDOWN.exists()
    assert GATE_JSON.exists()


def test_candidate_reality_gate_requires_validation_layers():
    gate = _gate()

    assert gate["status"] == "required_for_future_candidates"
    assert gate["synthetic_tests_required"] is True
    assert gate["real_local_audio_validation_required"] is True
    assert gate["no_op_check_required"] is True
    assert gate["deep_search_decision_required"] is True
    assert gate["deep_search_stop_required_when_external_information_needed"] is True
    assert gate["safe_wording_check_required"] is True


def test_candidate_reality_gate_records_deep_search_values():
    assert _gate()["allowed_deep_search_decisions"] == [
        "not_needed_internal_repo_only",
        "needed_external_standards",
        "needed_current_library_behavior",
        "needed_platform_or_policy_claims",
        "needed_market_or_product_research",
        "needed_security_or_safety_policy_check",
    ]


def test_candidate_reality_gate_records_forbidden_claims():
    claims = {claim.casefold() for claim in _gate()["forbidden_claims"]}

    assert "watermark removal" in claims
    assert "fingerprint removal" in claims
    assert "detector bypass" in claims
    assert "provenance removal" in claims
    assert "source-attribution removal" in claims


def test_candidate_reality_gate_keeps_project_reborn_inert():
    boundary = _gate()["project_reborn_boundary"]

    assert boundary["text_inspection_allowed"] is True
    assert boundary["execute_source"] is False
    assert boundary["import_source"] is False
    assert boundary["copy_source"] is False
    assert boundary["package_source"] is False
    assert boundary["expose_source"] is False


def test_readme_and_safety_reference_candidate_reality_gate_requirements():
    readme = README.read_text(encoding="utf-8")
    safety = SAFETY.read_text(encoding="utf-8")

    assert "Candidate Reality Gate" in readme
    assert "Deep Search decision" in readme
    assert "real local audio validation" in readme
    assert "no-op check" in readme
    assert "Deep Search decision" in safety
    assert "Real local audio validation is required" in safety
    assert "implementation must stop" in safety
    assert "Synthetic tests alone are not enough" in safety


def test_gitignore_ignores_local_validation_outputs():
    ignored = GITIGNORE.read_text(encoding="utf-8")

    for pattern in (
        "validation_samples/",
        "validation_outputs/",
        "final_exports/",
        "v010_validation_outputs/",
        "dist/",
        "build/",
        "*.egg-info/",
    ):
        assert pattern in ignored
