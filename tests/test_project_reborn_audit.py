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
SOURCE_DRAWER = PROJECT_REBORN / "source_drawer"
AUDIT_JSON = PROJECT_REBORN / "audit" / "project_reborn_audit_map.json"
AUDIT_MARKDOWN = PROJECT_REBORN / "audit" / "PROJECT_REBORN_AUDIT_MAP.md"
FORBIDDEN_REVIEW_STATUSES = {
    "ready_to_use",
    "safe_to_import",
    "active_feature",
}
REQUIRED_AUDIT_FIELDS = {
    "audit_category",
    "audit_priority",
    "current_path",
    "historical_filename",
    "reborn_id",
    "recommendation",
    "review_status",
}


def _audit() -> dict:
    return json.loads(AUDIT_JSON.read_text(encoding="utf-8"))


def test_project_reborn_audit_tool_and_outputs_exist():
    assert (ROOT / "tools" / "project_reborn_audit.py").exists()
    assert AUDIT_JSON.exists()
    assert AUDIT_MARKDOWN.exists()


def test_project_reborn_audit_json_schema():
    audit = _audit()

    assert audit["project"] == "Project Reborn"
    assert audit["audit_type"] == "static_text_audit_only"
    assert isinstance(audit["summary"], dict)
    assert isinstance(audit["entries"], list)


def test_every_source_drawer_file_is_represented_in_audit():
    source_paths = {
        path.relative_to(ROOT).as_posix()
        for path in SOURCE_DRAWER.iterdir()
        if path.is_file()
    }
    audit_paths = {entry["current_path"] for entry in _audit()["entries"]}

    assert source_paths
    assert source_paths == audit_paths


def test_every_audit_entry_has_required_fields_and_allowed_status():
    for entry in _audit()["entries"]:
        assert REQUIRED_AUDIT_FIELDS <= set(entry)
        assert (ROOT / entry["current_path"]).exists()
        assert entry["review_status"] not in FORBIDDEN_REVIEW_STATUSES


def test_audit_markdown_contains_static_only_warning():
    text = AUDIT_MARKDOWN.read_text(encoding="utf-8")

    assert "This is a static audit only." in text
    assert "No Project Reborn code was executed" in text
    assert "No audit result makes a file safe to import." in text


def test_project_reborn_check_passes_with_audit():
    assert validate_project_reborn(ROOT) == []


def test_project_reborn_still_has_no_init_files():
    assert list(PROJECT_REBORN.rglob("__init__.py")) == []


def test_project_reborn_still_not_in_setuptools_package_discovery():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    includes = metadata["tool"]["setuptools"]["packages"]["find"]["include"]

    assert "audio_quality_humanizer*" in includes
    assert all("project_reborn" not in include for include in includes)
