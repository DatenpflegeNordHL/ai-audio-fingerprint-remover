from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_MARKDOWN = ROOT / "docs" / "design" / "REBORN_025_DEEP_REVIEW.md"
REVIEW_JSON = ROOT / "docs" / "design" / "reborn_025_deep_review.json"


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


def test_reborn_025_deep_review_files_exist():
    assert REVIEW_MARKDOWN.exists()
    assert REVIEW_JSON.exists()


def test_reborn_025_deep_review_statuses_and_decision():
    review = _review()

    assert review["reborn_id"] == "reborn_025"
    assert review["status"] == "deep_review_design_only"
    assert review["implementation_status"] == "deferred"
    assert review["deep_search_decision"] == "not_needed_internal_repo_only"
    assert review["deep_search_stop_required"] is True


def test_reborn_025_deep_review_safe_ideas_and_rejections():
    review = _review()
    safe_ideas = " ".join(review["safe_ideas"]).casefold()
    rejected_ideas = " ".join(review["rejected_ideas"]).casefold()

    for expected in ("snr", "rmse", "correlation", "dynamic range", "spectral"):
        assert expected in safe_ideas

    for expected in ("detector", "watermark", "provenance", "recognition", "attribution"):
        assert expected in rejected_ideas


def test_reborn_025_deep_review_defers_runtime_changes():
    scope = _review()["future_scope"]
    review = _review()

    assert scope["new_cli_command"] is False
    assert scope["dsp_change"] is False
    assert scope["scoring_change"] is False
    assert scope["humanize_change"] is False
    assert scope["requires_candidate_reality_gate"] is True
    assert scope["requires_real_local_audio_validation"] is True
    assert scope["requires_no_op_check"] is True
    assert review["future_synthetic_tests"]
    assert review["future_real_audio_validation"]
    assert review["no_op_check_plan"]
    assert review["proposed_v0_11_scope"]


def test_reborn_025_deep_review_does_not_activate_project_reborn():
    review = _review()
    boundary = review["project_reborn_boundary"]

    assert boundary["reference_only"] is True
    assert boundary["execute_source"] is False
    assert boundary["import_source"] is False
    assert boundary["copy_source"] is False
    assert boundary["package_source"] is False
    assert boundary["expose_source"] is False

    all_strings = [item.casefold() for item in _flatten_strings(review)]
    assert review["implementation_status"] != "implemented"
    assert review["status"] != "implemented"
    assert not any("project reborn is safe to import" in item for item in all_strings)
