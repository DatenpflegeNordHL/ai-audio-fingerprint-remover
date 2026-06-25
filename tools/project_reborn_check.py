"""Validate that Project Reborn is cataloged and inert."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECT_REBORN_DIR = ROOT / "project_reborn"
SOURCE_DRAWER_DIR = PROJECT_REBORN_DIR / "source_drawer"
CATALOG_JSON = PROJECT_REBORN_DIR / "catalog" / "project_reborn_catalog.json"
CATALOG_MARKDOWN = PROJECT_REBORN_DIR / "catalog" / "PROJECT_REBORN_CATALOG.md"
AUDIT_JSON = PROJECT_REBORN_DIR / "audit" / "project_reborn_audit_map.json"
AUDIT_MARKDOWN = PROJECT_REBORN_DIR / "audit" / "PROJECT_REBORN_AUDIT_MAP.md"
PLAN_JSON = PROJECT_REBORN_DIR / "planning" / "project_reborn_top5_plan.json"
PLAN_MARKDOWN = PROJECT_REBORN_DIR / "planning" / "PROJECT_REBORN_TOP5_PLAN.md"
DESIGN_JSON = ROOT / "docs" / "design" / "v0_10_0_design_spec.json"
DESIGN_MARKDOWN = ROOT / "docs" / "design" / "V0_10_0_DESIGN_SPEC.md"
README = PROJECT_REBORN_DIR / "README.md"
REQUIRED_ENTRY_FIELDS = {
    "reborn_id",
    "current_path",
    "historical_filename",
    "status",
    "safe_review_category",
    "audit_category",
    "audit_priority",
    "review_status",
    "audit_report_path",
}
REQUIRED_AUDIT_ENTRY_FIELDS = {
    "audit_category",
    "audit_priority",
    "current_path",
    "historical_filename",
    "reborn_id",
    "recommendation",
    "review_status",
}
REQUIRED_PLAN_ENTRY_FIELDS = {
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
FORBIDDEN_REVIEW_STATUSES = {
    "ready_to_use",
    "safe_to_import",
    "active_feature",
}
FORBIDDEN_PLAN_NEXT_STEPS = {
    "ready_to_import",
    "active_feature",
    "already_safe",
}
ALLOWED_PLAN_NEXT_STEPS = {
    "candidate_for_v0_10_design",
    "needs_deeper_manual_review",
    "keep_as_reference_only",
    "discard_after_confirmation",
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
IMPLEMENTED_V0_10_CANDIDATES = {"reborn_008", "reborn_015", "reborn_022"}
DEFERRED_V0_10_CANDIDATES = {"reborn_025", "reborn_005"}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def validate_project_reborn(root: Path = ROOT) -> list[str]:
    """Return validation errors for the Project Reborn drawer."""

    errors: list[str] = []
    project_dir = root / "project_reborn"
    source_drawer = project_dir / "source_drawer"
    catalog_json = project_dir / "catalog" / "project_reborn_catalog.json"
    catalog_markdown = project_dir / "catalog" / "PROJECT_REBORN_CATALOG.md"
    audit_json = project_dir / "audit" / "project_reborn_audit_map.json"
    audit_markdown = project_dir / "audit" / "PROJECT_REBORN_AUDIT_MAP.md"
    plan_json = project_dir / "planning" / "project_reborn_top5_plan.json"
    plan_markdown = project_dir / "planning" / "PROJECT_REBORN_TOP5_PLAN.md"
    design_json = root / "docs" / "design" / "v0_10_0_design_spec.json"
    design_markdown = root / "docs" / "design" / "V0_10_0_DESIGN_SPEC.md"
    readme = project_dir / "README.md"

    for path in (
        readme,
        catalog_json,
        catalog_markdown,
        audit_json,
        audit_markdown,
        plan_json,
        plan_markdown,
        design_json,
        design_markdown,
        source_drawer,
    ):
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

    if audit_json.exists():
        _validate_audit(root, audit_json, source_drawer, errors)

    if plan_json.exists() and plan_markdown.exists():
        _validate_plan(root, plan_json, plan_markdown, errors)

    if design_json.exists() and design_markdown.exists():
        _validate_design_spec(root, design_json, design_markdown, errors)

    for path in project_dir.rglob("__init__.py"):
        errors.append(f"Project Reborn must not contain __init__.py: {path.relative_to(root)}")

    _validate_not_imported_by_package(root, errors)
    _validate_not_in_cli_help(errors)
    _validate_not_packaged(root, errors)
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


def _validate_audit(root: Path, audit_json: Path, source_drawer: Path, errors: list[str]) -> None:
    audit = _load_catalog(audit_json, errors)
    if audit is None:
        return
    entries = audit.get("entries", [])
    if not isinstance(entries, list):
        errors.append("Audit entries must be a list.")
        entries = []

    entry_by_path: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("Audit entry must be an object.")
            continue
        missing = sorted(field for field in REQUIRED_AUDIT_ENTRY_FIELDS if not entry.get(field))
        if missing:
            errors.append(f"Audit entry missing required fields {missing}: {entry}")
        current_path = entry.get("current_path")
        if isinstance(current_path, str):
            entry_by_path[current_path] = entry
            if not (root / current_path).exists():
                errors.append(f"Audit current_path does not exist: {current_path}")
        else:
            errors.append(f"Audit entry current_path must be a string: {entry}")
        if entry.get("review_status") in FORBIDDEN_REVIEW_STATUSES:
            errors.append(
                f"Audit entry {entry.get('reborn_id')} uses forbidden review_status: {entry.get('review_status')}"
            )

    if source_drawer.exists():
        for path in sorted(item for item in source_drawer.iterdir() if item.is_file()):
            relative_path = path.relative_to(root).as_posix()
            if relative_path not in entry_by_path:
                errors.append(f"Missing audit entry for {relative_path}")


def _validate_plan(root: Path, plan_json: Path, plan_markdown: Path, errors: list[str]) -> None:
    plan = _load_catalog(plan_json, errors)
    if plan is None:
        return

    if plan.get("project") != "Project Reborn":
        errors.append("Top-5 plan project must be Project Reborn.")
    if plan.get("plan_type") != "top5_manual_review_plan":
        errors.append("Top-5 plan plan_type must be top5_manual_review_plan.")
    if plan.get("review_method") != "manual_text_only":
        errors.append("Top-5 plan review_method must be manual_text_only.")

    entries = plan.get("top5", [])
    if not isinstance(entries, list):
        errors.append("Top-5 plan entries must be a list.")
        entries = []
    if len(entries) != 5:
        errors.append(f"Top-5 plan must contain exactly 5 entries, found {len(entries)}.")

    ranks: set[int] = set()
    reborn_ids: set[str] = set()
    next_step_counts = {step: 0 for step in ALLOWED_PLAN_NEXT_STEPS}
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("Top-5 plan entry must be an object.")
            continue
        _validate_plan_entry(root, entry, ranks, reborn_ids, next_step_counts, errors)

    if ranks and ranks != {1, 2, 3, 4, 5}:
        errors.append(f"Top-5 plan ranks must be 1 through 5, found {sorted(ranks)}.")

    summary = plan.get("selection_summary", {})
    if not isinstance(summary, dict):
        errors.append("Top-5 plan selection_summary must be an object.")
    else:
        if summary.get("reviewed_entries") != 5:
            errors.append("Top-5 plan selection_summary.reviewed_entries must be 5.")
        if summary.get("selected_top5") != 5:
            errors.append("Top-5 plan selection_summary.selected_top5 must be 5.")
        for step, count in next_step_counts.items():
            if summary.get(step, 0) != count:
                errors.append(
                    f"Top-5 plan selection_summary.{step} must match entry count {count}."
                )

    _validate_no_plan_claims("Top-5 plan JSON", json.dumps(plan, sort_keys=True), errors)
    _validate_no_plan_claims(
        "Top-5 plan markdown",
        plan_markdown.read_text(encoding="utf-8"),
        errors,
    )


def _validate_plan_entry(
    root: Path,
    entry: dict[str, Any],
    ranks: set[int],
    reborn_ids: set[str],
    next_step_counts: dict[str, int],
    errors: list[str],
) -> None:
    missing = sorted(field for field in REQUIRED_PLAN_ENTRY_FIELDS if not entry.get(field))
    if missing:
        errors.append(f"Top-5 plan entry missing required fields {missing}: {entry}")

    rank = entry.get("rank")
    if isinstance(rank, int):
        ranks.add(rank)
    else:
        errors.append(f"Top-5 plan entry rank must be an integer: {entry}")

    reborn_id = entry.get("reborn_id")
    if isinstance(reborn_id, str):
        if reborn_id in reborn_ids:
            errors.append(f"Top-5 plan contains duplicate reborn_id: {reborn_id}")
        reborn_ids.add(reborn_id)
    else:
        errors.append(f"Top-5 plan entry reborn_id must be a string: {entry}")

    current_path = entry.get("current_path")
    if isinstance(current_path, str):
        if not (root / current_path).exists():
            errors.append(f"Top-5 plan current_path does not exist: {current_path}")
    else:
        errors.append(f"Top-5 plan entry current_path must be a string: {entry}")

    next_step = entry.get("next_step")
    if next_step in FORBIDDEN_PLAN_NEXT_STEPS:
        errors.append(f"Top-5 plan entry {reborn_id} uses forbidden next_step: {next_step}")
    if next_step not in ALLOWED_PLAN_NEXT_STEPS:
        errors.append(f"Top-5 plan entry {reborn_id} uses unknown next_step: {next_step}")
    else:
        next_step_counts[next_step] += 1

    for list_field in ("manual_text_evidence", "safe_observed_ideas", "ignore_parts"):
        value = entry.get(list_field)
        if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
            errors.append(f"Top-5 plan entry {reborn_id} {list_field} must be a non-empty string list.")


def _validate_no_plan_claims(label: str, text: str, errors: list[str]) -> None:
    lowered = text.casefold()
    for claim in sorted(FORBIDDEN_PLAN_CLAIMS):
        if claim in lowered:
            errors.append(f"{label} contains forbidden planning claim: {claim}")


def _validate_design_spec(root: Path, design_json: Path, design_markdown: Path, errors: list[str]) -> None:
    design = _load_catalog(design_json, errors)
    if design is None:
        return

    if design.get("version_target") != "0.10.0":
        errors.append("v0.10 design spec version_target must be 0.10.0.")
    if design.get("status") != "safe_core_implemented":
        errors.append("v0.10 design spec status must be safe_core_implemented.")
    if design.get("active_package") != "audio-quality-humanizer":
        errors.append("v0.10 design spec active_package must be audio-quality-humanizer.")

    source_documents = design.get("source_documents", [])
    if not isinstance(source_documents, list):
        errors.append("v0.10 design spec source_documents must be a list.")
        source_documents = []
    for relative_path in source_documents:
        if not isinstance(relative_path, str):
            errors.append("v0.10 design spec source_documents entries must be strings.")
            continue
        if not (root / relative_path).exists():
            errors.append(f"v0.10 design spec source document does not exist: {relative_path}")

    implemented = _candidate_ids(design.get("implemented_candidates", []), "implemented_candidates", errors)
    deferred = _candidate_ids(design.get("deferred_candidates", []), "deferred_candidates", errors)
    if implemented != IMPLEMENTED_V0_10_CANDIDATES:
        errors.append(
            "v0.10 design spec implemented candidates must be "
            f"{sorted(IMPLEMENTED_V0_10_CANDIDATES)}, found {sorted(implemented)}."
        )
    if deferred != DEFERRED_V0_10_CANDIDATES:
        errors.append(
            "v0.10 design spec deferred candidates must be "
            f"{sorted(DEFERRED_V0_10_CANDIDATES)}, found {sorted(deferred)}."
        )

    markdown_text = design_markdown.read_text(encoding="utf-8")
    for required_text in (
        "Status: implemented safe core",
        "Candidate 1",
        "Candidate 2",
        "Candidate 3",
        "Candidate 4",
        "Candidate 5",
        "No Project Reborn source code was copied, imported, executed, packaged, or exposed",
    ):
        if required_text not in markdown_text:
            errors.append(f"v0.10 design markdown missing required text: {required_text}")


def _candidate_ids(value: Any, label: str, errors: list[str]) -> set[str]:
    if not isinstance(value, list):
        errors.append(f"v0.10 design spec {label} must be a list.")
        return set()
    ids: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            errors.append(f"v0.10 design spec {label} entries must be objects.")
            continue
        reborn_id = item.get("reborn_id")
        if not isinstance(reborn_id, str):
            errors.append(f"v0.10 design spec {label} entry missing reborn_id: {item}")
            continue
        ids.add(reborn_id)
    return ids


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


def _validate_not_packaged(root: Path, errors: list[str]) -> None:
    pyproject_text = (root / "pyproject.toml").read_text(encoding="utf-8")
    if "project_reborn*" in pyproject_text or 'project_reborn' in _package_include_block(pyproject_text):
        errors.append("pyproject package discovery must not include Project Reborn.")

    dist_dir = root / "dist"
    if dist_dir.exists():
        for wheel in dist_dir.glob("*.whl"):
            with zipfile.ZipFile(wheel) as archive:
                if any(name.startswith("project_reborn/") for name in archive.namelist()):
                    errors.append(f"Project Reborn files found in wheel: {wheel.relative_to(root)}")


def _package_include_block(pyproject_text: str) -> str:
    marker = "[tool.setuptools.packages.find]"
    if marker not in pyproject_text:
        return ""
    block = pyproject_text.split(marker, 1)[1]
    next_section = block.find("\n[")
    if next_section != -1:
        block = block[:next_section]
    return block


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
