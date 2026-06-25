"""Evaluate existing conservative presets on output copies."""

from __future__ import annotations

from pathlib import Path

from audio_quality_humanizer.analysis.compare import compare_audio
from audio_quality_humanizer.analysis.release_check import release_check
from audio_quality_humanizer.metadata.cleaner import sha256_file
from audio_quality_humanizer.processing.humanize import humanize_audio
from audio_quality_humanizer.reports.json_report import write_json_report
from audio_quality_humanizer.workflows.doctor import doctor_file


DEFAULT_PRESETS = ("subtle", "balanced", "club", "vocal", "afro-club")
PREFERENCE_PRESETS = ("subtle", "balanced", "vocal", "club", "afro-club")
PREFERENCE_ORDER = {name: index for index, name in enumerate(PREFERENCE_PRESETS)}


def preset_eval(
    input_path: Path,
    output_dir: Path,
    target: str = "streaming",
    presets: list[str] | None = None,
) -> dict:
    """Run selected presets on copies and recommend the safest eligible result."""

    input_path = Path(input_path)
    output_dir = Path(output_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"Output path is not a directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    selected_presets = presets if presets is not None else list(DEFAULT_PRESETS)
    original_hash = sha256_file(input_path)
    doctor = doctor_file(input_path, target=target)
    results = []
    warnings = []

    for preset_name in selected_presets:
        result = _evaluate_one_preset(input_path, output_dir, target, preset_name, original_hash)
        results.append(result)

    if sha256_file(input_path) != original_hash:
        warnings.append("Original input hash changed during preset evaluation.")

    recommended = _recommend(results)
    if recommended is None:
        recommended_preset = None
        recommendation_reason = "No preset was eligible because all evaluated outputs failed safety, compare, release checks, or original-file integrity checks."
    else:
        recommended_preset = recommended["preset"]
        recommendation_reason = (
            f"{recommended_preset} ranked highest by release score, compare score, "
            "warning count, and conservative preset preference."
        )

    return {
        "action": "preset_eval",
        "target": target,
        "input": str(input_path),
        "output_dir": str(output_dir),
        "presets": selected_presets,
        "doctor": doctor,
        "results": results,
        "recommended_preset": recommended_preset,
        "recommendation_reason": recommendation_reason,
        "warnings": warnings,
        "notes": [
            "Preset evaluation creates processed copies only and never modifies the original input.",
            "Preset evaluation compares conservative audio-quality and release-readiness outcomes only.",
            "Preset evaluation does not evaluate or alter watermarks, fingerprints, detector signals, provenance markers, origin markers, C2PA markers, or attribution systems.",
            "Recommendation logic is not legal clearance or platform certification.",
        ],
    }


def _evaluate_one_preset(
    input_path: Path,
    output_dir: Path,
    target: str,
    preset_name: str,
    original_hash: str,
) -> dict:
    safe_preset_name = _safe_label(preset_name)
    output_path = _numbered_path(output_dir / f"{input_path.stem}.{safe_preset_name}.humanized{input_path.suffix}")
    report_path = _numbered_path(output_dir / f"{input_path.stem}.{safe_preset_name}.eval.json")
    result = {
        "preset": preset_name,
        "output": str(output_path),
        "report": str(report_path),
        "humanize_passed": False,
        "humanize_reverted": False,
        "compare_passed": False,
        "compare_score": None,
        "release_passed": False,
        "release_score": None,
        "blocking_issues": [],
        "warnings": [],
        "recommendations": [],
        "error": None,
    }

    try:
        humanize_report = humanize_audio(input_path, output_path, preset=preset_name, target=target)
        compare_report = compare_audio(input_path, output_path, target=target)
        release_report = release_check(output_path, target=target)
        input_unchanged = sha256_file(input_path) == original_hash

        result.update(
            {
                "humanize_passed": bool(humanize_report.get("passed")),
                "humanize_reverted": bool(humanize_report.get("reverted")),
                "compare_passed": bool(compare_report.get("passed")),
                "compare_score": compare_report.get("score"),
                "release_passed": bool(release_report.get("passed")),
                "release_score": release_report.get("score"),
                "blocking_issues": _blocking_issues(
                    humanize_report,
                    compare_report,
                    release_report,
                    input_unchanged,
                ),
                "warnings": _warnings(humanize_report, compare_report, release_report),
                "recommendations": _recommendations(humanize_report, compare_report, release_report),
            }
        )
        write_json_report(
            {
                "action": "preset_eval_result",
                "result": result,
                "humanize": humanize_report,
                "compare": compare_report,
                "release_check": release_report,
            },
            report_path,
        )
    except Exception as exc:
        result["error"] = str(exc)
        result["blocking_issues"] = [str(exc)]
        write_json_report({"action": "preset_eval_result", "result": result}, report_path)

    return result


def _blocking_issues(humanize_report: dict, compare_report: dict, release_report: dict, input_unchanged: bool) -> list[str]:
    issues = []
    issues.extend(humanize_report.get("safety", {}).get("blocking_issues", []))
    issues.extend(item.get("message", "") for item in compare_report.get("regressions", []) if item.get("severity") == "blocking")
    issues.extend(release_report.get("blocking_issues", []))
    if not input_unchanged:
        issues.append("Original input hash changed during preset evaluation.")
    return _dedupe([issue for issue in issues if issue])


def _warnings(humanize_report: dict, compare_report: dict, release_report: dict) -> list[str]:
    values = []
    values.extend(humanize_report.get("safety", {}).get("warnings", []))
    values.extend(compare_report.get("warnings", []))
    values.extend(release_report.get("warnings", []))
    return _dedupe(values)


def _recommendations(humanize_report: dict, compare_report: dict, release_report: dict) -> list[str]:
    values = []
    values.extend(humanize_report.get("safety", {}).get("recommendations", []))
    values.extend(compare_report.get("recommendations", []))
    values.extend(release_report.get("recommendations", []))
    return _dedupe(values)


def _recommend(results: list[dict]) -> dict | None:
    eligible = [result for result in results if _is_eligible(result)]
    if not eligible:
        return None
    return sorted(
        eligible,
        key=lambda result: (
            -(result.get("release_score") or 0),
            -(result.get("compare_score") or 0),
            len(result.get("warnings", [])),
            PREFERENCE_ORDER.get(result["preset"], len(PREFERENCE_ORDER)),
        ),
    )[0]


def _is_eligible(result: dict) -> bool:
    output = result.get("output")
    return (
        result.get("humanize_passed") is True
        and result.get("humanize_reverted") is False
        and result.get("compare_passed") is True
        and not result.get("blocking_issues")
        and output is not None
        and Path(output).exists()
    )


def _safe_label(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def _numbered_path(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(1, 10_000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not create a safe numbered filename for {path}")


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
