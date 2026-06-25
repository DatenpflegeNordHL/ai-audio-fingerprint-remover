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

DESIGN_MARKDOWN = ROOT / "docs" / "design" / "V0_10_0_DESIGN_SPEC.md"
DESIGN_JSON = ROOT / "docs" / "design" / "v0_10_0_design_spec.json"
PROJECT_REBORN = ROOT / "project_reborn"
IMPLEMENTED = {"reborn_008", "reborn_015", "reborn_022"}
DEFERRED = {"reborn_025", "reborn_005"}


def _design() -> dict:
    return json.loads(DESIGN_JSON.read_text(encoding="utf-8"))


def test_v0_10_design_spec_files_exist():
    assert DESIGN_MARKDOWN.exists()
    assert DESIGN_JSON.exists()


def test_v0_10_design_json_records_implemented_and_deferred_candidates():
    design = _design()

    assert design["version_target"] == "0.10.0"
    assert design["status"] == "safe_core_implemented"
    assert design["active_package"] == "audio-quality-humanizer"
    assert set(design["source_documents"]) == {
        "project_reborn/planning/PROJECT_REBORN_TOP5_PLAN.md",
        "project_reborn/audit/PROJECT_REBORN_AUDIT_MAP.md",
        "docs/design/CANDIDATE_REALITY_GATE.md",
        "docs/design/REBORN_025_DEEP_REVIEW.md",
    }
    assert {item["reborn_id"] for item in design["implemented_candidates"]} == IMPLEMENTED
    assert {item["reborn_id"] for item in design["deferred_candidates"]} == DEFERRED
    assert design["candidate_reality_gate"]["deep_search_decision_required"] is True
    assert design["candidate_reality_gate"]["deep_search_stop_required_when_external_information_needed"] is True
    assert design["candidate_reality_gate"]["real_local_audio_validation_required"] is True
    assert design["candidate_reality_gate"]["no_op_check_required"] is True
    assert design["candidate_reality_gate"]["safe_wording_check_required"] is True


def test_v0_10_design_markdown_records_safe_boundaries():
    text = DESIGN_MARKDOWN.read_text(encoding="utf-8")

    assert "Status: implemented safe core" in text
    assert "Candidate 1, `reborn_008`, is implemented" in text
    assert "Candidate 4, `reborn_025`, is deferred" in text
    assert "Candidate Reality Gate" in text
    assert "Deep Search stop rule" in text
    assert "real local audio validation" in text
    assert "no-op checks" in text
    assert "No Project Reborn source code was copied, imported, executed, packaged, or exposed" in text


def test_project_reborn_check_passes_with_v0_10_design_spec():
    assert validate_project_reborn(ROOT) == []


def test_project_reborn_remains_excluded_from_package_discovery():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    includes = metadata["tool"]["setuptools"]["packages"]["find"]["include"]

    assert "audio_quality_humanizer*" in includes
    assert all("project_reborn" not in include for include in includes)


def test_project_reborn_has_no_init_files_after_v0_10():
    assert list(PROJECT_REBORN.rglob("__init__.py")) == []


def test_active_package_does_not_import_project_reborn():
    package_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "audio_quality_humanizer").rglob("*.py"))
    )

    assert "project_reborn" not in package_sources
    assert "Project Reborn" not in package_sources
