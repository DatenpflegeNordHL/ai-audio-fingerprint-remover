from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.project_reborn_check import validate_project_reborn

PROJECT_REBORN = ROOT / "project_reborn"
PLAN_JSON = PROJECT_REBORN / "planning" / "project_reborn_top5_plan.json"
PLAN_MARKDOWN = PROJECT_REBORN / "planning" / "PROJECT_REBORN_TOP5_PLAN.md"
FORBIDDEN_NEXT_STEPS = {
    "ready_to_import",
    "active_feature",
    "already_safe",
}
FORBIDDEN_PLAN_CLAIMS = {
    "safe to import",
    "safe-to-import",
    "ready to import",
    "ready-to-import",
    "already safe",
    "active feature",
    "safe_to_import",
    "ready_to_import",
    "already_safe",
    "active_feature",
}
REQUIRED_TOP5_FIELDS = {
    "rank",
    "reborn_id",
    "current_path",
    "historical_filename",
    "audit_category",
    "audit_priority",
    "future_module",
    "feature_direction",
    "complexity",
    "dependency_risk",
    "safety_risk",
    "manual_text_evidence",
    "safe_observed_ideas",
    "ignore_parts",
    "recommendation",
    "next_step",
}


def _plan() -> dict:
    return json.loads(PLAN_JSON.read_text(encoding="utf-8"))


def test_project_reborn_top5_plan_files_exist():
    assert PLAN_JSON.exists()
    assert PLAN_MARKDOWN.exists()


def test_project_reborn_top5_plan_schema_and_selection():
    plan = _plan()

    assert plan["project"] == "Project Reborn"
    assert plan["plan_type"] == "top5_manual_review_plan"
    assert plan["review_method"] == "manual_text_only"
    assert plan["source_audit"] == "project_reborn/audit/project_reborn_audit_map.json"
    assert len(plan["top5"]) == 5
    assert [entry["rank"] for entry in plan["top5"]] == [1, 2, 3, 4, 5]
    assert {entry["reborn_id"] for entry in plan["top5"]} == {
        "reborn_008",
        "reborn_015",
        "reborn_022",
        "reborn_025",
        "reborn_005",
    }


def test_every_top5_entry_has_required_fields_and_safe_status():
    for entry in _plan()["top5"]:
        assert REQUIRED_TOP5_FIELDS <= set(entry)
        assert (ROOT / entry["current_path"]).exists()
        assert entry["next_step"] not in FORBIDDEN_NEXT_STEPS
        assert isinstance(entry["manual_text_evidence"], list) and entry["manual_text_evidence"]
        assert isinstance(entry["safe_observed_ideas"], list) and entry["safe_observed_ideas"]
        assert isinstance(entry["ignore_parts"], list) and entry["ignore_parts"]


def test_top5_plan_does_not_claim_files_are_import_ready():
    combined = json.dumps(_plan(), sort_keys=True).casefold()
    combined += "\n" + PLAN_MARKDOWN.read_text(encoding="utf-8").casefold()

    for claim in FORBIDDEN_PLAN_CLAIMS:
        assert claim not in combined


def test_project_reborn_check_passes_with_top5_plan():
    assert validate_project_reborn(ROOT) == []


def test_project_reborn_top5_still_has_no_init_files():
    assert list(PROJECT_REBORN.rglob("__init__.py")) == []


def test_project_reborn_top5_still_not_in_setuptools_package_discovery():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    includes = metadata["tool"]["setuptools"]["packages"]["find"]["include"]

    assert "audio_quality_humanizer*" in includes
    assert all("project_reborn" not in include for include in includes)
