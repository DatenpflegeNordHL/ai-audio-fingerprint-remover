"""Local validation setup diagnostics."""

from __future__ import annotations

from pathlib import Path


REPORT_NAMES = {
    "validation.md",
    "validation.json",
    "preset_eval.json",
    "preset_eval.md",
}
REPORT_SUFFIXES = (
    ".validation.json",
    ".eval.json",
)


def validation_status(root: Path | None = None, find: bool = False, max_depth: int = 4) -> dict:
    """Inspect local validation paths without reading audio content."""

    cwd = Path.cwd().resolve()
    inspected_root = (root or cwd).expanduser().resolve()
    found_reports = _find_reports(inspected_root, max_depth) if find else []
    report = {
        "action": "validation_status",
        "root": str(inspected_root),
        "cwd": str(cwd),
        "looks_like_project_root": _looks_like_project_root(inspected_root),
        "project_root_hint": _format_optional_path(_find_project_root_hint(inspected_root) or _find_project_root_hint(cwd)),
        "venv_python_exists": (inspected_root / ".venv" / "bin" / "python").exists(),
        "venv_cli_exists": (inspected_root / ".venv" / "bin" / "ai-humanizer").exists(),
        "validation_manifest_exists": (inspected_root / "validation_manifest.json").exists(),
        "validation_json_exists": (inspected_root / "validation.json").exists(),
        "validation_markdown_exists": (inspected_root / "validation.md").exists(),
        "validation_samples_dir_exists": (inspected_root / "validation_samples").is_dir(),
        "validation_outputs_dir_exists": (inspected_root / "validation_outputs").is_dir(),
        "found_reports": found_reports,
        "suggested_commands": [],
        "warnings": [],
        "notes": [
            "Validation samples and outputs are local and gitignored by design.",
            "This command is diagnostic only.",
            "It does not read or process audio.",
            (
                "It does not evaluate or alter watermarks, fingerprints, detector signals, "
                "provenance markers, origin markers, C2PA markers, or attribution systems."
            ),
        ],
    }

    warnings = report["warnings"]
    if not report["looks_like_project_root"]:
        warnings.append("Inspected root does not look like the project root.")
    if not report["venv_python_exists"]:
        warnings.append(".venv/bin/python was not found under the inspected root.")
    if not report["venv_cli_exists"]:
        warnings.append(".venv/bin/ai-humanizer was not found under the inspected root.")
    if not report["validation_manifest_exists"]:
        warnings.append("validation_manifest.json was not found under the inspected root.")
    if not report["validation_markdown_exists"] and not report["validation_json_exists"]:
        warnings.append("validation.md and validation.json were not found under the inspected root.")

    report["suggested_commands"] = _suggest_commands(report)
    return report


def _looks_like_project_root(path: Path) -> bool:
    return (
        (path / "pyproject.toml").is_file()
        and (path / "audio_quality_humanizer").is_dir()
        and (path / "README.md").is_file()
    )


def _find_project_root_hint(path: Path) -> Path | None:
    resolved = path.expanduser().resolve()
    candidates = [resolved, *resolved.parents]
    for candidate in candidates:
        if _looks_like_project_root(candidate):
            return candidate
    return None


def _find_reports(root: Path, max_depth: int) -> list[str]:
    max_depth = max(0, max_depth)
    found: list[Path] = []
    _collect_reports(root.expanduser().resolve(), root.expanduser().resolve(), max_depth, found)
    return [str(path) for path in sorted(found)]


def _collect_reports(root: Path, current: Path, max_depth: int, found: list[Path]) -> None:
    depth = len(current.relative_to(root).parts)
    if depth > max_depth:
        return
    for child in current.iterdir():
        if child.is_file() and _is_report_file(child):
            found.append(child)
        elif child.is_dir() and depth < max_depth:
            _collect_reports(root, child, max_depth, found)


def _is_report_file(path: Path) -> bool:
    name = path.name
    return name in REPORT_NAMES or any(name.endswith(suffix) for suffix in REPORT_SUFFIXES)


def _suggest_commands(report: dict) -> list[str]:
    commands: list[str] = []
    root_hint = report.get("project_root_hint")
    if not report.get("looks_like_project_root") and root_hint:
        commands.append(f"cd {root_hint}")

    if report.get("venv_python_exists"):
        commands.append(".venv/bin/python tools/cli_smoke.py")
        commands.append(
            ".venv/bin/ai-humanizer validate-samples validation_manifest.json "
            "--output-dir validation_outputs --default-target club --report validation.json --markdown validation.md"
        )
    else:
        commands.append('python3 -m pip install -e ".[test]"')
        commands.append("python3 -m pytest")

    if not report.get("validation_manifest_exists"):
        commands.append("cp examples/validation_manifest.example.json validation_manifest.json")
        commands.append("mkdir -p validation_samples validation_outputs")

    if not report.get("validation_markdown_exists") and not report.get("validation_json_exists"):
        commands.append(
            ".venv/bin/ai-humanizer validate-samples validation_manifest.json "
            "--output-dir validation_outputs --default-target club --report validation.json --markdown validation.md"
        )

    found_reports = report.get("found_reports", [])
    if found_reports:
        if report.get("validation_markdown_exists"):
            commands.append("cat validation.md")
        commands.append(f"cat {found_reports[0]}")
    return _dedupe(commands)


def _format_optional_path(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(path)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped
