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
CANDIDATE_GATE_JSON = ROOT / "docs" / "design" / "candidate_reality_gate.json"
CANDIDATE_GATE_MARKDOWN = ROOT / "docs" / "design" / "CANDIDATE_REALITY_GATE.md"
REBORN_025_REVIEW_JSON = ROOT / "docs" / "design" / "reborn_025_deep_review.json"
REBORN_025_REVIEW_MARKDOWN = ROOT / "docs" / "design" / "REBORN_025_DEEP_REVIEW.md"
REBORN_005_REVIEW_JSON = ROOT / "docs" / "design" / "reborn_005_deep_review.json"
REBORN_005_REVIEW_MARKDOWN = ROOT / "docs" / "design" / "REBORN_005_DEEP_REVIEW.md"
V0_11_COMPARE_JSON = ROOT / "docs" / "design" / "v0_11_0_compare_metrics.json"
V0_11_COMPARE_MARKDOWN = ROOT / "docs" / "design" / "V0_11_0_COMPARE_METRICS.md"
V0_11_RELEASE_NOTES = ROOT / "docs" / "releases" / "V0_11_0_RELEASE_NOTES.md"
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
REQUIRED_V0_11_COMPARE_METRICS = {
    "rmse",
    "mean_absolute_error",
    "correlation",
    "snr_db_approx",
    "peak_before",
    "peak_after",
    "peak_delta",
    "rms_before",
    "rms_after",
    "rms_delta",
    "dynamic_range_before_db",
    "dynamic_range_after_db",
    "dynamic_range_delta_db",
    "spectral_centroid_before_hz",
    "spectral_centroid_after_hz",
    "spectral_centroid_delta_hz",
    "spectral_rolloff_before_hz",
    "spectral_rolloff_after_hz",
    "spectral_rolloff_delta_hz",
}
FORBIDDEN_V0_11_METRIC_NAMES = {
    "watermark_score",
    "fingerprint_score",
    "detector_score",
    "evasion_score",
    "bypass_score",
    "recognition_score",
    "provenance_score",
    "detectability_score",
    "origin_score",
    "source_attribution_score",
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
    audit_json = project_dir / "audit" / "project_reborn_audit_map.json"
    audit_markdown = project_dir / "audit" / "PROJECT_REBORN_AUDIT_MAP.md"
    plan_json = project_dir / "planning" / "project_reborn_top5_plan.json"
    plan_markdown = project_dir / "planning" / "PROJECT_REBORN_TOP5_PLAN.md"
    design_json = root / "docs" / "design" / "v0_10_0_design_spec.json"
    design_markdown = root / "docs" / "design" / "V0_10_0_DESIGN_SPEC.md"
    candidate_gate_json = root / "docs" / "design" / "candidate_reality_gate.json"
    candidate_gate_markdown = root / "docs" / "design" / "CANDIDATE_REALITY_GATE.md"
    reborn_025_review_json = root / "docs" / "design" / "reborn_025_deep_review.json"
    reborn_025_review_markdown = root / "docs" / "design" / "REBORN_025_DEEP_REVIEW.md"
    reborn_005_review_json = root / "docs" / "design" / "reborn_005_deep_review.json"
    reborn_005_review_markdown = root / "docs" / "design" / "REBORN_005_DEEP_REVIEW.md"
    v0_11_compare_json = root / "docs" / "design" / "v0_11_0_compare_metrics.json"
    v0_11_compare_markdown = root / "docs" / "design" / "V0_11_0_COMPARE_METRICS.md"
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
        candidate_gate_json,
        candidate_gate_markdown,
        reborn_025_review_json,
        reborn_025_review_markdown,
        reborn_005_review_json,
        reborn_005_review_markdown,
        v0_11_compare_json,
        v0_11_compare_markdown,
        root / "docs" / "releases" / "V0_11_0_RELEASE_NOTES.md",
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

    if candidate_gate_json.exists() and candidate_gate_markdown.exists():
        _validate_candidate_reality_gate(candidate_gate_json, candidate_gate_markdown, errors)

    if reborn_025_review_json.exists() and reborn_025_review_markdown.exists():
        _validate_reborn_025_deep_review(reborn_025_review_json, reborn_025_review_markdown, errors)

    if reborn_005_review_json.exists() and reborn_005_review_markdown.exists():
        _validate_reborn_005_deep_review(reborn_005_review_json, reborn_005_review_markdown, errors)

    if v0_11_compare_json.exists() and v0_11_compare_markdown.exists():
        _validate_v0_11_compare_metrics(v0_11_compare_json, v0_11_compare_markdown, errors)

    v0_11_release_notes = root / "docs" / "releases" / "V0_11_0_RELEASE_NOTES.md"
    if v0_11_release_notes.exists():
        _validate_v0_11_release_notes(v0_11_release_notes, errors)

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

    gate = plan.get("candidate_reality_gate", {})
    if not isinstance(gate, dict):
        errors.append("Top-5 plan candidate_reality_gate must be an object.")
    else:
        _validate_required_true(
            gate,
            (
                "deep_search_decision_required",
                "deep_search_stop_required_when_external_information_needed",
                "synthetic_tests_required",
                "real_local_audio_validation_required",
                "no_op_check_required",
                "safe_wording_check_required",
            ),
            "Top-5 plan candidate_reality_gate",
            errors,
        )

    review = plan.get("reborn_025_deep_review", {})
    if not isinstance(review, dict):
        errors.append("Top-5 plan reborn_025_deep_review must be an object.")
    else:
        if review.get("status") != "deep_review_design_only":
            errors.append("Top-5 plan reborn_025_deep_review status must be deep_review_design_only.")
        if review.get("implementation_status") != "safe_rewrite_implemented_v0_11_0":
            errors.append(
                "Top-5 plan reborn_025_deep_review implementation_status must be safe_rewrite_implemented_v0_11_0."
            )
        if review.get("deep_search_stop_required") is not True:
            errors.append("Top-5 plan reborn_025_deep_review deep_search_stop_required must be true.")

    v0_11_status = plan.get("v0_11_status", {})
    if not isinstance(v0_11_status, dict):
        errors.append("Top-5 plan v0_11_status must be an object.")
    else:
        if v0_11_status.get("reborn_025") != "safe_read_only_compare_metrics_rewritten_from_first_principles":
            errors.append("Top-5 plan v0_11_status must record reborn_025 safe read-only rewrite.")
        if v0_11_status.get("reborn_005") != "deep_review_design_only_deferred_pending_separate_approval":
            errors.append("Top-5 plan v0_11_status must record reborn_005 design-only deferred review.")

    review_005 = plan.get("reborn_005_deep_review", {})
    if not isinstance(review_005, dict):
        errors.append("Top-5 plan reborn_005_deep_review must be an object.")
    else:
        if review_005.get("status") != "deep_review_design_only":
            errors.append("Top-5 plan reborn_005_deep_review status must be deep_review_design_only.")
        if review_005.get("implementation_status") != "deferred":
            errors.append("Top-5 plan reborn_005_deep_review implementation_status must be deferred.")
        if review_005.get("deep_search_decision") != "not_needed_internal_repo_only":
            errors.append("Top-5 plan reborn_005_deep_review deep_search_decision must be not_needed_internal_repo_only.")
        if review_005.get("deep_search_stop_required") is not True:
            errors.append("Top-5 plan reborn_005_deep_review deep_search_stop_required must be true.")
        for key in (
            "future_implementation_requires_separate_approval",
            "future_implementation_requires_candidate_reality_gate",
            "future_implementation_requires_real_local_audio_validation_if_user_facing_behavior_changes",
            "future_implementation_requires_no_op_check_if_user_facing_behavior_changes",
        ):
            if review_005.get(key) is not True:
                errors.append(f"Top-5 plan reborn_005_deep_review.{key} must be true.")


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
        "Candidate Reality Gate",
        "real local audio validation",
        "no-op check",
        "No Project Reborn source code was copied, imported, executed, packaged, or exposed",
    ):
        if required_text not in markdown_text:
            errors.append(f"v0.10 design markdown missing required text: {required_text}")

    gate = design.get("candidate_reality_gate", {})
    if not isinstance(gate, dict):
        errors.append("v0.10 design spec candidate_reality_gate must be an object.")
    else:
        _validate_required_true(
            gate,
            (
                "deep_search_decision_required",
                "deep_search_stop_required_when_external_information_needed",
                "synthetic_tests_required",
                "real_local_audio_validation_required",
                "no_op_check_required",
                "safe_wording_check_required",
            ),
            "v0.10 design spec candidate_reality_gate",
            errors,
        )

    for item in design.get("deferred_candidates", []):
        if isinstance(item, dict) and item.get("reborn_id") == "reborn_025":
            if item.get("deep_review_status") != "deep_review_design_only":
                errors.append("v0.10 design spec reborn_025 deep_review_status must be deep_review_design_only.")
            if item.get("implementation_status") != "deferred":
                errors.append("v0.10 design spec reborn_025 implementation_status must be deferred.")
        if isinstance(item, dict) and item.get("reborn_id") == "reborn_005":
            if item.get("deep_review_status") != "deep_review_design_only":
                errors.append("v0.10 design spec reborn_005 deep_review_status must be deep_review_design_only.")
            if item.get("implementation_status") != "deferred":
                errors.append("v0.10 design spec reborn_005 implementation_status must be deferred.")
            for key in (
                "future_implementation_requires_separate_approval",
                "future_implementation_requires_candidate_reality_gate",
                "future_implementation_requires_real_local_audio_validation_if_user_facing_behavior_changes",
                "future_implementation_requires_no_op_check_if_user_facing_behavior_changes",
            ):
                if item.get(key) is not True:
                    errors.append(f"v0.10 design spec reborn_005 {key} must be true.")


def _validate_candidate_reality_gate(
    gate_json: Path,
    gate_markdown: Path,
    errors: list[str],
) -> None:
    gate = _load_catalog(gate_json, errors)
    if gate is None:
        return
    if gate.get("status") != "required_for_future_candidates":
        errors.append("Candidate Reality Gate status must be required_for_future_candidates.")
    _validate_required_true(
        gate,
        (
            "deep_search_decision_required",
            "deep_search_stop_required_when_external_information_needed",
            "synthetic_tests_required",
            "real_local_audio_validation_required",
            "no_op_check_required",
            "safe_wording_check_required",
        ),
        "Candidate Reality Gate",
        errors,
    )
    forbidden_claims = gate.get("forbidden_claims", [])
    if not isinstance(forbidden_claims, list) or not forbidden_claims:
        errors.append("Candidate Reality Gate forbidden_claims must be a non-empty list.")
    allowed_decisions = gate.get("allowed_deep_search_decisions", [])
    if allowed_decisions != [
        "not_needed_internal_repo_only",
        "needed_external_standards",
        "needed_current_library_behavior",
        "needed_platform_or_policy_claims",
        "needed_market_or_product_research",
        "needed_security_or_safety_policy_check",
    ]:
        errors.append("Candidate Reality Gate allowed_deep_search_decisions do not match required values.")
    boundary = gate.get("project_reborn_boundary", {})
    if not isinstance(boundary, dict):
        errors.append("Candidate Reality Gate project_reborn_boundary must be an object.")
    else:
        for key in ("execute_source", "import_source", "copy_source", "package_source", "expose_source"):
            if boundary.get(key) is not False:
                errors.append(f"Candidate Reality Gate project_reborn_boundary.{key} must be false.")

    markdown = gate_markdown.read_text(encoding="utf-8")
    for required_text in (
        "Deep Search decision",
        "Synthetic tests are required, but not sufficient.",
        "A user-facing audio candidate must be tested with at least one local user-supplied audio file.",
        "A no-op check must prove that unchanged input stays unchanged",
        "Generated local validation outputs must stay ignored and uncommitted",
    ):
        if required_text not in markdown:
            errors.append(f"Candidate Reality Gate markdown missing required text: {required_text}")


def _validate_reborn_025_deep_review(
    review_json: Path,
    review_markdown: Path,
    errors: list[str],
) -> None:
    review = _load_catalog(review_json, errors)
    if review is None:
        return
    if review.get("reborn_id") != "reborn_025":
        errors.append("reborn_025 deep review reborn_id must be reborn_025.")
    if review.get("status") != "deep_review_design_only":
        errors.append("reborn_025 deep review status must be deep_review_design_only.")
    if review.get("implementation_status") != "safe_rewrite_implemented_v0_11_0":
        errors.append("reborn_025 deep review implementation_status must be safe_rewrite_implemented_v0_11_0.")
    if review.get("deep_search_decision") != "not_needed_internal_repo_only":
        errors.append("reborn_025 deep review deep_search_decision must be not_needed_internal_repo_only.")
    if review.get("deep_search_stop_required") is not True:
        errors.append("reborn_025 deep review deep_search_stop_required must be true.")
    for key in ("future_synthetic_tests", "future_real_audio_validation", "no_op_check_plan", "proposed_v0_11_scope"):
        value = review.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"reborn_025 deep review {key} must be a non-empty list.")
    scope = review.get("future_scope", {})
    if not isinstance(scope, dict):
        errors.append("reborn_025 deep review future_scope must be an object.")
    else:
        for key in ("new_cli_command", "dsp_change", "scoring_change", "humanize_change"):
            if scope.get(key) is not False:
                errors.append(f"reborn_025 deep review future_scope.{key} must be false.")
        for key in (
            "requires_candidate_reality_gate",
            "requires_real_local_audio_validation",
            "requires_no_op_check",
        ):
            if scope.get(key) is not True:
                errors.append(f"reborn_025 deep review future_scope.{key} must be true.")
    boundary = review.get("project_reborn_boundary", {})
    if not isinstance(boundary, dict):
        errors.append("reborn_025 deep review project_reborn_boundary must be an object.")
    else:
        for key in ("execute_source", "import_source", "copy_source", "package_source", "expose_source"):
            if boundary.get(key) is not False:
                errors.append(f"reborn_025 deep review project_reborn_boundary.{key} must be false.")

    review_text = json.dumps(review, sort_keys=True).casefold()
    if "ready_to_import" in review_text or "active_feature" in review_text:
        errors.append("reborn_025 deep review must not mark Project Reborn as active or import-ready.")

    markdown = review_markdown.read_text(encoding="utf-8")
    for required_text in (
        "Manual text-only review. Design only. No implementation.",
        "Safe read-only implementation completed in v0.11.0",
        "`not_needed_internal_repo_only`",
        "If future implementation needs current external standards",
        "No Project Reborn source was executed, imported, copied, packaged, or exposed",
    ):
        if required_text not in markdown:
            errors.append(f"reborn_025 deep review markdown missing required text: {required_text}")


def _validate_reborn_005_deep_review(
    review_json: Path,
    review_markdown: Path,
    errors: list[str],
) -> None:
    review = _load_catalog(review_json, errors)
    if review is None:
        return
    if review.get("reborn_id") != "reborn_005":
        errors.append("reborn_005 deep review reborn_id must be reborn_005.")
    if review.get("status") != "deep_review_design_only":
        errors.append("reborn_005 deep review status must be deep_review_design_only.")
    if review.get("implementation_status") != "deferred":
        errors.append("reborn_005 deep review implementation_status must be deferred.")
    if review.get("deep_search_decision") != "not_needed_internal_repo_only":
        errors.append("reborn_005 deep review deep_search_decision must be not_needed_internal_repo_only.")
    if review.get("deep_search_stop_required") is not True:
        errors.append("reborn_005 deep review deep_search_stop_required must be true.")

    for key in (
        "source_inspection",
        "possible_future_scope",
        "project_reborn_boundary",
    ):
        if not isinstance(review.get(key), dict):
            errors.append(f"reborn_005 deep review {key} must be an object.")

    for key in (
        "safe_ideas",
        "rejected_ideas",
        "future_synthetic_tests",
        "future_real_audio_validation",
        "no_op_check_plan",
    ):
        value = review.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"reborn_005 deep review {key} must be a non-empty list.")

    source = review.get("source_inspection", {})
    if isinstance(source, dict):
        if source.get("method") != "manual_text_only":
            errors.append("reborn_005 deep review source_inspection.method must be manual_text_only.")
        for key in ("executed", "imported", "copied", "packaged", "exposed"):
            if source.get(key) is not False:
                errors.append(f"reborn_005 deep review source_inspection.{key} must be false.")

    scope = review.get("possible_future_scope", {})
    if isinstance(scope, dict):
        for key in (
            "active_implementation_approved",
            "new_cli_behavior_approved",
            "metadata_cleanup_changes_approved",
            "audio_processing_changes_approved",
            "release_check_scoring_changes_approved",
        ):
            if scope.get(key) is not False:
                errors.append(f"reborn_005 deep review possible_future_scope.{key} must be false.")
        for key in (
            "requires_separate_approval",
            "requires_candidate_reality_gate",
            "requires_real_local_audio_validation_if_user_facing_behavior_changes",
            "requires_no_op_check_if_user_facing_behavior_changes",
        ):
            if scope.get(key) is not True:
                errors.append(f"reborn_005 deep review possible_future_scope.{key} must be true.")

    boundary = review.get("project_reborn_boundary", {})
    if isinstance(boundary, dict):
        if boundary.get("reference_only") is not True:
            errors.append("reborn_005 deep review project_reborn_boundary.reference_only must be true.")
        for key in ("executed", "imported", "copied", "packaged", "exposed"):
            if boundary.get(key) is not False:
                errors.append(f"reborn_005 deep review project_reborn_boundary.{key} must be false.")

    safe_text = " ".join(review.get("safe_ideas", [])).casefold()
    for unsafe in ("removal", "bypass", "detector", "provenance"):
        if unsafe in safe_text:
            errors.append(f"reborn_005 deep review safe_ideas must not include unsafe concept: {unsafe}")

    rejected_text = " ".join(review.get("rejected_ideas", [])).casefold()
    for required in ("fingerprint", "watermark", "detector", "provenance", "attribution", "bypass", "evasion", "detectability"):
        if required not in rejected_text:
            errors.append(f"reborn_005 deep review rejected_ideas missing required concept: {required}")

    review_text = json.dumps(review, sort_keys=True).casefold()
    if "safe to import" in review_text or "ready_to_import" in review_text or "active_feature" in review_text:
        errors.append("reborn_005 deep review must not mark Project Reborn as active or import-ready.")

    markdown = review_markdown.read_text(encoding="utf-8")
    for required_text in (
        "Manual text-only review. Design only. No implementation.",
        "`not_needed_internal_repo_only`",
        "No Project Reborn source was executed, imported, copied, packaged, or exposed.",
        "Implementation remains deferred.",
        "No active package code changes are approved by this review.",
    ):
        if required_text not in markdown:
            errors.append(f"reborn_005 deep review markdown missing required text: {required_text}")


def _validate_v0_11_compare_metrics(
    design_json: Path,
    design_markdown: Path,
    errors: list[str],
) -> None:
    design = _load_catalog(design_json, errors)
    if design is None:
        return
    if design.get("version_target") != "0.11.0":
        errors.append("v0.11 compare metrics version_target must be 0.11.0.")
    if design.get("status") != "implemented_safe_read_only_compare_metrics":
        errors.append("v0.11 compare metrics status must be implemented_safe_read_only_compare_metrics.")
    if design.get("deep_search_decision") != "not_needed_internal_repo_only":
        errors.append("v0.11 compare metrics deep_search_decision must be not_needed_internal_repo_only.")
    if design.get("deep_search_stop_rule_active") is not True:
        errors.append("v0.11 compare metrics deep_search_stop_rule_active must be true.")

    boundary = design.get("safety_boundary", {})
    if not isinstance(boundary, dict):
        errors.append("v0.11 compare metrics safety_boundary must be an object.")
    else:
        for key in (
            "new_cli_command",
            "audio_modification",
            "release_check_scoring_change",
            "humanize_processing_change",
            "project_reborn_source_copied",
            "project_reborn_source_imported",
            "project_reborn_source_executed",
            "project_reborn_source_packaged",
            "project_reborn_source_exposed",
        ):
            if boundary.get(key) is not False:
                errors.append(f"v0.11 compare metrics safety_boundary.{key} must be false.")

    implemented_metrics = set(design.get("implemented_metrics", []))
    if not REQUIRED_V0_11_COMPARE_METRICS <= implemented_metrics:
        missing = sorted(REQUIRED_V0_11_COMPARE_METRICS - implemented_metrics)
        errors.append(f"v0.11 compare metrics missing required metrics: {missing}")

    rejected_names = set(design.get("rejected_metric_names", []))
    if not FORBIDDEN_V0_11_METRIC_NAMES <= rejected_names:
        missing = sorted(FORBIDDEN_V0_11_METRIC_NAMES - rejected_names)
        errors.append(f"v0.11 compare metrics missing rejected metric names: {missing}")

    validation = design.get("real_local_validation_plan", {})
    if not isinstance(validation, dict):
        errors.append("v0.11 compare metrics real_local_validation_plan must be an object.")
    else:
        if validation.get("required") is not True:
            errors.append("v0.11 compare metrics real local validation must be required.")
        if validation.get("commit_outputs") is not False:
            errors.append("v0.11 compare metrics validation outputs must not be committed.")

    no_op = design.get("no_op_check_plan", {})
    if not isinstance(no_op, dict) or no_op.get("required") is not True:
        errors.append("v0.11 compare metrics no-op check must be required.")

    markdown = design_markdown.read_text(encoding="utf-8")
    for required_text in (
        "Implemented safe read-only compare metric expansion.",
        "`not_needed_internal_repo_only`",
        "No Project Reborn source code was copied, imported, executed, packaged, or exposed",
        "Generated validation reports and generated audio must stay ignored and uncommitted.",
    ):
        if required_text not in markdown:
            errors.append(f"v0.11 compare metrics markdown missing required text: {required_text}")


def _validate_v0_11_release_notes(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for required_text in (
        "Version: `0.11.0`",
        "Release type: safe read-only compare metrics",
        "comparison_metrics",
        "Project Reborn source was not copied, imported, executed, packaged, or exposed.",
    ):
        if required_text not in text:
            errors.append(f"v0.11 release notes missing required text: {required_text}")
    if "/Users/" in text:
        errors.append("v0.11 release notes must not include local absolute paths.")


def _validate_required_true(
    data: dict[str, Any],
    keys: tuple[str, ...],
    label: str,
    errors: list[str],
) -> None:
    for key in keys:
        if data.get(key) is not True:
            errors.append(f"{label}.{key} must be true.")


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
