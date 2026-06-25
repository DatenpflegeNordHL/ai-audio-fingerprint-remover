from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
PROJECT_REBORN = ROOT / "project_reborn"
SOURCE_DRAWER = PROJECT_REBORN / "source_drawer"
CATALOG_JSON = PROJECT_REBORN / "catalog" / "project_reborn_catalog.json"
CATALOG_MARKDOWN = PROJECT_REBORN / "catalog" / "PROJECT_REBORN_CATALOG.md"


def _catalog_entries() -> list[dict]:
    catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    return catalog["entries"]


def test_project_reborn_required_files_exist():
    assert (PROJECT_REBORN / "README.md").exists()
    assert SOURCE_DRAWER.exists()
    assert CATALOG_JSON.exists()
    assert CATALOG_MARKDOWN.exists()


def test_project_reborn_has_no_init_files():
    assert list(PROJECT_REBORN.rglob("__init__.py")) == []


def test_project_reborn_not_in_setuptools_package_discovery():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    includes = metadata["tool"]["setuptools"]["packages"]["find"]["include"]

    assert "audio_quality_humanizer*" in includes
    assert all("project_reborn" not in include for include in includes)


def test_every_source_drawer_file_has_catalog_entry():
    source_files = {
        path.relative_to(ROOT).as_posix()
        for path in SOURCE_DRAWER.iterdir()
        if path.is_file()
    }
    catalog_paths = {entry["current_path"] for entry in _catalog_entries()}

    assert source_files
    assert source_files == catalog_paths


def test_every_catalog_entry_is_reference_only_and_inert():
    for entry in _catalog_entries():
        assert (ROOT / entry["current_path"]).exists()
        assert entry["status"] == "reference_only_not_installed"
        assert entry["imported_by_package"] is False
        assert entry["exposed_by_cli"] is False
        assert entry["included_in_wheel"] is False


def test_readme_and_safety_reference_project_reborn():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    safety = (ROOT / "SAFETY.md").read_text(encoding="utf-8")

    assert "Project Reborn" in readme
    assert "Project Reborn" in safety
