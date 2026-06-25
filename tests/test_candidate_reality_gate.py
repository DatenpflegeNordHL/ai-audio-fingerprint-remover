from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE_MARKDOWN = ROOT / "docs" / "design" / "CANDIDATE_REALITY_GATE.md"
GATE_JSON = ROOT / "docs" / "design" / "candidate_reality_gate.json"
README = ROOT / "README.md"
SAFETY = ROOT / "SAFETY.md"


def _gate() -> dict:
    return json.loads(GATE_JSON.read_text(encoding="utf-8"))


def test_candidate_reality_gate_files_exist():
    assert GATE_MARKDOWN.exists()
    assert GATE_JSON.exists()


def test_candidate_reality_gate_requires_validation_layers():
    gate = _gate()

    assert gate["status"] == "required_for_future_candidates"
    assert gate["synthetic_tests_required"] is True
    assert gate["real_local_audio_validation_required_for_user_facing_audio_behavior"] is True
    assert gate["no_op_check_required_for_user_facing_audio_behavior"] is True
    assert gate["deep_search_decision_required"] is True
    assert gate["generated_local_validation_outputs_must_stay_ignored"] is True


def test_candidate_reality_gate_records_forbidden_claims():
    claims = {claim.casefold() for claim in _gate()["forbidden_claims"]}

    assert "watermark removal" in claims
    assert "fingerprint removal" in claims
    assert "detector bypass" in claims
    assert "provenance suppression" in claims
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
    assert "no-op checks" in readme
    assert "Deep Search decision" in safety
    assert "Real local audio validation is required" in safety
    assert "Synthetic tests alone are not enough" in safety
