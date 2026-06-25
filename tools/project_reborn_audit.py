"""Generate a static Project Reborn audit map.

This tool only reads Project Reborn files as bytes/text. It never imports,
executes, or shells out to source drawer files.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROJECT_REBORN_DIR = ROOT / "project_reborn"
SOURCE_DRAWER_DIR = PROJECT_REBORN_DIR / "source_drawer"
CATALOG_JSON = PROJECT_REBORN_DIR / "catalog" / "project_reborn_catalog.json"
CATALOG_MARKDOWN = PROJECT_REBORN_DIR / "catalog" / "PROJECT_REBORN_CATALOG.md"
AUDIT_DIR = PROJECT_REBORN_DIR / "audit"
AUDIT_JSON = AUDIT_DIR / "project_reborn_audit_map.json"
AUDIT_MARKDOWN = AUDIT_DIR / "PROJECT_REBORN_AUDIT_MAP.md"

SAFE_TERM_CANDIDATES = {
    "audio_quality_cleanup": (
        "rms",
        "peak",
        "clipping",
        "lufs",
        "spectral",
        "stereo",
        "phase",
        "harshness",
        "mud",
        "dynamic range",
        "waveform",
        "normalize",
        "eq",
        "filter",
        "denoise",
    ),
    "sound_relief": (
        "harshness",
        "mud",
        "overload",
        "clip",
        "distortion",
        "smooth",
        "loudness",
    ),
    "metadata_privacy_cleanup": (
        "metadata",
        "tag",
        "privacy",
        "exif",
        "comment",
        "artist",
        "album",
    ),
    "conservative_repair": (
        "repair",
        "restore",
        "fix",
        "cleanup",
        "safety",
        "validate",
    ),
    "mix_diagnostics": (
        "mix",
        "diagnostic",
        "analysis",
        "rms",
        "peak",
        "spectral",
        "stereo",
        "phase",
    ),
    "release_readiness": (
        "release",
        "readiness",
        "streaming",
        "youtube",
        "club",
        "threshold",
    ),
    "comparison": (
        "compare",
        "comparison",
        "diff",
        "delta",
        "before",
        "after",
        "similarity",
    ),
    "performance": (
        "performance",
        "optimize",
        "benchmark",
        "timing",
        "speed",
        "cache",
        "profile",
    ),
    "reporting": (
        "report",
        "summary",
        "json",
        "markdown",
        "table",
    ),
}

RISK_TERMS = (
    "watermark",
    "fingerprint",
    "detector",
    "recognition",
    "bypass",
    "evasion",
    "undetectable",
    "provenance",
    "origin marker",
    "c2pa",
    "attribution",
)

STD_LIB_IMPORTS = {
    "argparse",
    "ast",
    "collections",
    "contextlib",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "functools",
    "hashlib",
    "io",
    "itertools",
    "json",
    "logging",
    "math",
    "os",
    "pathlib",
    "random",
    "re",
    "shutil",
    "statistics",
    "subprocess",
    "sys",
    "tempfile",
    "time",
    "typing",
    "uuid",
    "wave",
    "zipfile",
}

FORBIDDEN_REVIEW_STATUSES = {
    "ready_to_use",
    "safe_to_import",
    "active_feature",
}


def main() -> int:
    catalog = _read_json(CATALOG_JSON)
    entries_by_path = {
        entry["current_path"]: entry
        for entry in catalog.get("entries", [])
        if isinstance(entry, dict) and "current_path" in entry
    }
    audit_entries = []
    for path in sorted(item for item in SOURCE_DRAWER_DIR.iterdir() if item.is_file()):
        relative_path = path.relative_to(ROOT).as_posix()
        catalog_entry = entries_by_path.get(relative_path, {})
        audit_entries.append(_audit_file(path, catalog_entry))

    audit = {
        "project": "Project Reborn",
        "audit_type": "static_text_audit_only",
        "active_package": "audio-quality-humanizer",
        "principle": "Old filenames are historical labels only and must not be used to infer behavior.",
        "safety_boundary": [
            "Project Reborn is not imported.",
            "Project Reborn is not packaged.",
            "Project Reborn is not exposed through CLI.",
            "No Project Reborn code was executed during this audit.",
        ],
        "summary": _summary(audit_entries),
        "entries": audit_entries,
    }

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    AUDIT_MARKDOWN.write_text(_render_markdown(audit), encoding="utf-8")
    _update_catalog(catalog, audit_entries)
    _write_catalog_markdown(catalog)
    print(f"Project Reborn audit map written for {len(audit_entries)} file(s).")
    return 0


def _audit_file(path: Path, catalog_entry: dict[str, Any]) -> dict[str, Any]:
    data = path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    text = _decode_text(data)
    static_parse_status = "binary_or_unreadable"
    tree: ast.AST | None = None
    parse_error = None
    if text is not None:
        if path.suffix == ".py":
            try:
                tree = ast.parse(text)
                static_parse_status = "parsed_ast"
            except SyntaxError as exc:
                static_parse_status = "parse_error"
                parse_error = f"{exc.__class__.__name__}: {exc.msg}"
        else:
            static_parse_status = "text_only"

    imports = _top_level_imports(tree) if tree is not None else []
    function_names = _function_names(tree) if tree is not None else []
    class_names = _class_names(tree) if tree is not None else []
    text_for_scan = text or ""
    candidates, safe_terms = _safe_candidates(text_for_scan, path, function_names)
    risk_terms = _matched_terms(text_for_scan, RISK_TERMS)
    category = _audit_category(candidates)
    priority = _audit_priority(candidates, category, static_parse_status)
    review_status = _review_status(category, priority)
    recommendation = _recommendation(category, candidates, priority)
    notes = ["Static text observations only; file was not imported or executed."]
    if parse_error:
        notes.append(parse_error)
    if risk_terms:
        notes.append("Risk terms are text-observation flags for manual review, not behavior claims.")

    return {
        "reborn_id": catalog_entry.get("reborn_id", path.stem),
        "current_path": path.relative_to(ROOT).as_posix(),
        "historical_filename": catalog_entry.get("historical_filename", ""),
        "file_type": catalog_entry.get("file_type", _file_type(path)),
        "sha256": sha256,
        "size_bytes": len(data),
        "line_count": _line_count(text),
        "static_parse_status": static_parse_status,
        "top_level_imports": imports,
        "function_names": function_names,
        "class_names": class_names,
        "obvious_entrypoint_present": 'if __name__ == "__main__"' in text_for_scan
        or "if __name__ == '__main__'" in text_for_scan,
        "external_dependency_names": _external_dependencies(imports),
        "notable_safe_terms": safe_terms,
        "notable_risk_terms": risk_terms,
        "safe_future_use_candidates": candidates,
        "audit_category": category,
        "audit_priority": priority,
        "review_status": review_status,
        "recommendation": recommendation,
        "notes": notes,
    }


def _decode_text(data: bytes) -> str | None:
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("latin-1")
        except UnicodeDecodeError:
            return None


def _top_level_imports(tree: ast.AST) -> list[str]:
    imports: list[str] = []
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Import):
            imports.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    return sorted(set(imports))


def _function_names(tree: ast.AST) -> list[str]:
    names = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    return sorted(set(names))


def _class_names(tree: ast.AST) -> list[str]:
    names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return sorted(set(names))


def _external_dependencies(imports: list[str]) -> list[str]:
    return sorted(
        item
        for item in set(imports)
        if item not in STD_LIB_IMPORTS
        and item not in {"audio_quality_humanizer", "project_reborn"}
        and not item.startswith("_")
    )


def _safe_candidates(text: str, path: Path, function_names: list[str]) -> tuple[list[str], list[str]]:
    normalized = _normalize(text)
    candidates: list[str] = []
    safe_terms: list[str] = []
    if path.suffix in {".md", ".txt", ".html"}:
        candidates.append("documentation_notes")
    if _looks_like_tests(normalized, function_names):
        candidates.append("test_ideas")
    for candidate, terms in SAFE_TERM_CANDIDATES.items():
        matched = [term for term in terms if _has_term(normalized, term)]
        if matched:
            candidates.append(candidate)
            safe_terms.extend(matched)
    if not candidates:
        candidates.append("unknown_review_needed")
    return sorted(set(candidates)), sorted(set(safe_terms))


def _looks_like_tests(normalized: str, function_names: list[str]) -> bool:
    return (
        any(name.startswith("test_") for name in function_names)
        or "pytest" in normalized
        or "unittest" in normalized
        or " assert " in normalized
    )


def _matched_terms(text: str, terms: tuple[str, ...]) -> list[str]:
    normalized = _normalize(text)
    return sorted(term for term in terms if _has_term(normalized, term))


def _normalize(text: str) -> str:
    return re.sub(r"[\s_-]+", " ", text.casefold())


def _has_term(normalized_text: str, term: str) -> bool:
    normalized_term = re.escape(_normalize(term)).replace(r"\ ", r"\s+")
    return re.search(r"\b" + normalized_term + r"\b", normalized_text) is not None


def _audit_category(candidates: list[str]) -> str:
    if "test_ideas" in candidates:
        return "test_reference"
    if "documentation_notes" in candidates and len(candidates) == 1:
        return "documentation_reference"
    if "metadata_privacy_cleanup" in candidates:
        return "metadata_privacy_reference"
    if "comparison" in candidates:
        return "comparison_reference"
    if "performance" in candidates:
        return "performance_reference"
    if "reporting" in candidates:
        return "report_reference"
    if any(
        candidate in candidates
        for candidate in (
            "audio_quality_cleanup",
            "sound_relief",
            "conservative_repair",
            "mix_diagnostics",
            "release_readiness",
        )
    ):
        return "audio_quality_reference"
    if "documentation_notes" in candidates:
        return "documentation_reference"
    return "unknown_reference"


def _audit_priority(candidates: list[str], category: str, static_parse_status: str) -> str:
    if "discard_candidate" in candidates or category == "discard_candidate":
        return "discard"
    if static_parse_status == "binary_or_unreadable":
        return "medium"
    high_candidates = {
        "audio_quality_cleanup",
        "sound_relief",
        "metadata_privacy_cleanup",
        "conservative_repair",
        "mix_diagnostics",
        "release_readiness",
        "comparison",
        "performance",
    }
    if any(candidate in high_candidates for candidate in candidates):
        return "high"
    if "unknown_review_needed" in candidates:
        return "medium"
    return "low"


def _review_status(category: str, priority: str) -> str:
    if priority == "discard" or category == "discard_candidate":
        return "discard_candidate"
    if priority == "high":
        return "candidate_for_safe_rewrite"
    if priority == "low":
        return "static_audit_only"
    return "needs_manual_review"


def _recommendation(category: str, candidates: list[str], priority: str) -> str:
    if priority == "discard":
        return "Likely discard after manual confirmation."
    if "metadata_privacy_cleanup" in candidates:
        return "Review manually for possible metadata/privacy cleanup ideas."
    if category == "audio_quality_reference":
        return "Review manually for possible safe rewrite into audio_quality_humanizer.analysis."
    if category == "comparison_reference":
        return "Review manually for possible comparison or report ideas."
    if category == "performance_reference":
        return "Review manually for possible performance ideas."
    if category == "test_reference":
        return "Review manually for test ideas only."
    if category == "documentation_reference":
        return "Keep as notes only unless manual review identifies safe documentation value."
    return "Needs manual review; do not infer behavior from historical filename."


def _summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    priority_counts = Counter(entry["audit_priority"] for entry in entries)
    category_counts = Counter(entry["audit_category"] for entry in entries)
    candidate_counts: Counter[str] = Counter()
    for entry in entries:
        candidate_counts.update(entry["safe_future_use_candidates"])
    return {
        "total_files": len(entries),
        "parsed_ast": sum(entry["static_parse_status"] == "parsed_ast" for entry in entries),
        "text_only": sum(entry["static_parse_status"] == "text_only" for entry in entries),
        "parse_errors": sum(entry["static_parse_status"] == "parse_error" for entry in entries),
        "binary_or_unreadable": sum(
            entry["static_parse_status"] == "binary_or_unreadable" for entry in entries
        ),
        "priority_counts": dict(sorted(priority_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "candidate_counts": dict(sorted(candidate_counts.items())),
    }


def _render_markdown(audit: dict[str, Any]) -> str:
    summary = audit["summary"]
    lines = [
        "# Project Reborn Audit Map",
        "",
        "## Purpose",
        "",
        "This is a static audit only. No Project Reborn code was executed, imported, packaged, or exposed through CLI.",
        "",
        "## Principle",
        "",
        "The old filename is not the package. Historical filenames are traceability labels only.",
        "",
        "Audit terms are review flags, not product claims. No audit result makes a file safe to import.",
        "",
        "## Summary",
        "",
        f"- Total files: {summary['total_files']}",
        f"- Parsed AST: {summary['parsed_ast']}",
        f"- Text only: {summary['text_only']}",
        f"- Parse errors: {summary['parse_errors']}",
        f"- Binary/unreadable: {summary['binary_or_unreadable']}",
    ]
    _count_table(lines, "Priority Counts", summary["priority_counts"], "Priority")
    _count_table(lines, "Category Counts", summary["category_counts"], "Category")
    _count_table(lines, "Candidate Counts", summary["candidate_counts"], "Candidate")
    lines.extend(
        [
            "",
            "## Entries",
            "",
            "| Reborn ID | Current Path | Historical Filename | Category | Priority | Review Status | Safe Future Use Candidates | Recommendation |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for entry in audit["entries"]:
        lines.append(
            "| "
            f"{entry['reborn_id']} | "
            f"`{entry['current_path']}` | "
            f"{entry['historical_filename']} | "
            f"{entry['audit_category']} | "
            f"{entry['audit_priority']} | "
            f"{entry['review_status']} | "
            f"{', '.join(entry['safe_future_use_candidates'])} | "
            f"{entry['recommendation']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _count_table(lines: list[str], title: str, values: dict[str, int], label: str) -> None:
    lines.extend(["", f"## {title}", "", f"| {label} | Count |", "| --- | --- |"])
    if not values:
        lines.append("| None | 0 |")
        return
    for key, count in values.items():
        lines.append(f"| {key} | {count} |")


def _update_catalog(catalog: dict[str, Any], audit_entries: list[dict[str, Any]]) -> None:
    audit_by_path = {entry["current_path"]: entry for entry in audit_entries}
    for entry in catalog.get("entries", []):
        audit_entry = audit_by_path.get(entry.get("current_path"))
        if not audit_entry:
            continue
        entry["audit_category"] = audit_entry["audit_category"]
        entry["audit_priority"] = audit_entry["audit_priority"]
        entry["review_status"] = audit_entry["review_status"]
        entry["safe_future_use_candidates"] = audit_entry["safe_future_use_candidates"]
        entry["audit_report_path"] = AUDIT_MARKDOWN.relative_to(ROOT).as_posix()
    CATALOG_JSON.write_text(json.dumps(catalog, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _write_catalog_markdown(catalog: dict[str, Any]) -> None:
    lines = [
        "# Project Reborn Catalog",
        "",
        "Project Reborn is a non-installed reference drawer for historical experimental scripts. It exists only to preserve material for future safe review.",
        "",
        "Safety boundary: nothing in Project Reborn is active product code, imported by `audio_quality_humanizer`, packaged into the wheel, or exposed through the CLI. No file in Project Reborn is trusted automatically.",
        "",
        "Principle: the old filename is not the package. Historical filenames are traceability labels only and must not be used to infer behavior. Future review must inspect behavior, not names.",
        "",
        "Any useful logic must be rewritten safely into the main package later, with tests, safety scan coverage, CLI smoke coverage, and build validation.",
        "",
        "Static audit map: `project_reborn/audit/PROJECT_REBORN_AUDIT_MAP.md`.",
        "",
        "| Reborn ID | Current Path | Historical Filename | Category | Status | Future Use Candidates | Audit Priority | Review Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in catalog.get("entries", []):
        lines.append(
            "| "
            f"{entry.get('reborn_id', '')} | "
            f"{entry.get('current_path', '')} | "
            f"{entry.get('historical_filename', '')} | "
            f"{entry.get('audit_category', entry.get('safe_review_category', 'unknown_reference'))} | "
            "reference only, not installed | "
            f"{', '.join(entry.get('safe_future_use_candidates', []))} | "
            f"{entry.get('audit_priority', '')} | "
            f"{entry.get('review_status', '')} |"
        )
    lines.extend(
        [
            "",
            "No file in Project Reborn is active product code.",
            "",
            "Any useful logic must be rewritten safely into the main package later.",
            "",
            "Future review must inspect behavior, not names.",
            "",
        ]
    )
    CATALOG_MARKDOWN.write_text("\n".join(lines), encoding="utf-8")


def _file_type(path: Path) -> str:
    if path.suffix == ".py":
        return "python"
    if path.suffix == ".md":
        return "markdown"
    if path.suffix == ".txt":
        return "text"
    if path.suffix == ".html":
        return "html"
    return "unknown"


def _line_count(text: str | None) -> int:
    if text is None:
        return 0
    if text == "":
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
