from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SAFETY = ROOT / "SAFETY.md"
REVIEW_MARKDOWN = ROOT / "docs" / "design" / "REBORN_005_DEEP_REVIEW.md"
REVIEW_JSON = ROOT / "docs" / "design" / "reborn_005_deep_review.json"


def _review() -> dict:
    return json.loads(REVIEW_JSON.read_text(encoding="utf-8"))


def _flatten_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_flatten_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(_flatten_strings(item))
        return strings
    return []


def test_reborn_005_deep_review_files_exist():
    assert REVIEW_MARKDOWN.exists()
    assert REVIEW_JSON.exists()


def test_reborn_005_deep_review_statuses_and_decision():
    review = _review()

    assert review["reborn_id"] == "reborn_005"
    assert review["status"] == "deep_review_design_only"
    assert review["implementation_status"] == "deferred"
    assert review["deep_search_decision"] == "not_needed_internal_repo_only"
    assert review["deep_search_stop_required"] is True


def test_reborn_005_source_inspection_is_text_only_and_inert():
    source = _review()["source_inspection"]

    assert source["path"] == "project_reborn/source_drawer/reborn_005_reference.py"
    assert source["method"] == "manual_text_only"
    assert source["executed"] is False
    assert source["imported"] is False
    assert source["copied"] is False
    assert source["packaged"] is False
    assert source["exposed"] is False


def test_reborn_005_safe_ideas_are_neutral_and_rejections_are_explicit():
    review = _review()
    safe_ideas = " ".join(review["safe_ideas"]).casefold()
    rejected_ideas = " ".join(review["rejected_ideas"]).casefold()

    for expected in ("metadata", "runtime", "operation timing", "spectral entropy", "spectral flatness", "chunked"):
        assert expected in safe_ideas

    for unsafe in ("removal", "bypass", "detector", "provenance", "watermark", "fingerprint", "attribution", "detectability"):
        assert unsafe not in safe_ideas

    for expected in ("fingerprint", "watermark", "detector", "provenance", "attribution", "bypass", "evasion", "detectability"):
        assert expected in rejected_ideas


def test_reborn_005_future_scope_does_not_approve_implementation():
    review = _review()
    scope = review["possible_future_scope"]

    assert scope["status"] == "design_only"
    assert scope["active_implementation_approved"] is False
    assert scope["new_cli_behavior_approved"] is False
    assert scope["metadata_cleanup_changes_approved"] is False
    assert scope["audio_processing_changes_approved"] is False
    assert scope["release_check_scoring_changes_approved"] is False
    assert scope["requires_separate_approval"] is True
    assert scope["requires_candidate_reality_gate"] is True
    assert scope["requires_real_local_audio_validation_if_user_facing_behavior_changes"] is True
    assert scope["requires_no_op_check_if_user_facing_behavior_changes"] is True


def test_reborn_005_project_reborn_boundary_stays_reference_only():
    review = _review()
    boundary = review["project_reborn_boundary"]

    assert boundary["reference_only"] is True
    assert boundary["executed"] is False
    assert boundary["imported"] is False
    assert boundary["copied"] is False
    assert boundary["packaged"] is False
    assert boundary["exposed"] is False

    all_strings = [item.casefold() for item in _flatten_strings(review)]
    assert not any("project reborn is safe to import" in item for item in all_strings)
    assert not any("ready_to_import" in item for item in all_strings)
    assert review["status"] != "implemented"
    assert review["implementation_status"] == "deferred"


def test_reborn_005_gate_plans_are_populated():
    review = _review()

    assert review["future_synthetic_tests"]
    assert review["future_real_audio_validation"]
    assert review["no_op_check_plan"]
    assert any("inspect-only commands do not modify files" in item for item in review["no_op_check_plan"])


def test_reborn_005_readme_and_safety_do_not_claim_active_behavior_changed():
    readme = README.read_text(encoding="utf-8")
    safety = SAFETY.read_text(encoding="utf-8")

    assert "No active package behavior changed from that review." in readme
    assert "`reborn_005` remains deferred after design-only review." in safety
    assert "No Project Reborn source was copied, imported, executed, packaged, or exposed during the `reborn_005` review." in safety
    assert "reborn_005` is implemented" not in readme
    assert "reborn_005` is implemented" not in safety
