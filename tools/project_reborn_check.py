"""Validate that Project Reborn is cataloged and inert."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECT_REBORN_DIR = ROOT / "project_reborn"
SOURCE_DRAWER_DIR = PROJECT_REBORN_DIR / "source_drawer"
CATALOG_JSON = PROJECT_REBORN_DIR / "catalog" / "project_reborn_catalog.json"
CATALOG_MARKDOWN = PROJECT_REBORN_DIR / "catalog" / "PROJECT_REBORN_CATALOG.md"
README = PROJECT_REBORN_DIR / "README.md"
REQUIRED_ENTRY_FIELDS = {
    "reborn_id",
    "current_path",
    "historical_filename",
    "status",
    "safe_review_category",
}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def validate_project_reborn(root: Path = ROOT) -> list[str]:
    """Return validation errors for the Project Reborn drawer."""

    errors: list[str] = []
    project_dir = root / "project_reborn"
    source_drawer = project_dir / "source_drawer"
    catalog_json = project_dir / "catalog" / "project_reborn_catalog.json"
    catalog_markdown = project_dir / "catalog" / "PROJECT_REBORN_CATALOG.md"
    readme = project_dir / "README.md"

    for path in (readme, catalog_json, catalog_markdown, source_drawer):
        if not path.exists():
            errors.append(f"Missing required Project Reborn path: {path.relative_to(root)}")

    if not catalog_json.exists():
        return errors

    catalog = _load_catalog(catalog_json, errors)
    if catalog is None:
        return errors

    entries = catalog.get("entries", [])
    if not isinstance(entries, list):
        errors.append("Catalog entries must be a list.")
        entries = []

    entry_by_path: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("Catalog entry must be an object.")
            continue
        _validate_entry(root, entry, errors)
        current_path = entry.get("current_path")
        if isinstance(current_path, str):
            entry_by_path[current_path] = entry

    if source_drawer.exists():
        for path in sorted(item for item in source_drawer.iterdir() if item.is_file()):
            relative_path = path.relative_to(root).as_posix()
            if relative_path not in entry_by_path:
                errors.append(f"Missing catalog entry for {relative_path}")

    for path in project_dir.rglob("__init__.py"):
        errors.append(f"Project Reborn must not contain __init__.py: {path.relative_to(root)}")

    _validate_not_imported_by_package(root, errors)
    _validate_not_in_cli_help(errors)
    return errors


def _load_catalog(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid Project Reborn catalog JSON: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append("Project Reborn catalog root must be an object.")
        return None
    return data


def _validate_entry(root: Path, entry: dict[str, Any], errors: list[str]) -> None:
    missing = sorted(field for field in REQUIRED_ENTRY_FIELDS if not entry.get(field))
    if missing:
        errors.append(f"Catalog entry missing required fields {missing}: {entry}")

    current_path = entry.get("current_path")
    if isinstance(current_path, str):
        if not (root / current_path).exists():
            errors.append(f"Catalog current_path does not exist: {current_path}")
    else:
        errors.append(f"Catalog entry current_path must be a string: {entry}")

    for key in ("imported_by_package", "exposed_by_cli", "included_in_wheel"):
        if entry.get(key) is not False:
            errors.append(f"Catalog entry {entry.get('reborn_id')} must set {key} to false.")


def _validate_not_imported_by_package(root: Path, errors: list[str]) -> None:
    package_dir = root / "audio_quality_humanizer"
    for path in sorted(package_dir.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "project_reborn" in source or "Project Reborn" in source:
            errors.append(f"Project Reborn reference found in package source: {path.relative_to(root)}")


def _validate_not_in_cli_help(errors: list[str]) -> None:
    from audio_quality_humanizer.cli import _build_parser

    parser = _build_parser()
    help_texts = [parser.format_help()]
    for action in parser._subparsers._actions:
        choices = getattr(action, "choices", None)
        if choices:
            help_texts.extend(subparser.format_help() for subparser in choices.values())
    combined = "\n".join(help_texts).casefold()
    if "project reborn" in combined or "project_reborn" in combined:
        errors.append("CLI help must not expose Project Reborn as a feature command.")


def main() -> int:
    errors = validate_project_reborn(ROOT)
    if errors:
        print("Project Reborn check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Project Reborn check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
