"""Run local validation over user-supplied audio samples."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from audio_quality_humanizer.analysis.release_check import SUPPORTED_TARGETS
from audio_quality_humanizer.metadata.cleaner import sha256_file
from audio_quality_humanizer.reports.json_report import write_json_report
from audio_quality_humanizer.validation.manifest import load_manifest, validate_manifest
from audio_quality_humanizer.workflows.doctor import doctor_file
from audio_quality_humanizer.workflows.preset_eval import DEFAULT_PRESETS, preset_eval


HIGH_DOCTOR_SCORE = 85
WARNING_HEAVY_THRESHOLD = 3


def run_validation(
    manifest_path: Path,
    output_dir: Path,
    default_target: str = "streaming",
    fail_fast: bool = False,
) -> dict:
    """Run doctor and preset evaluation for each manifest sample."""

    manifest_path = Path(manifest_path)
    output_dir = Path(output_dir)
    default_target = default_target.casefold()
    if default_target not in SUPPORTED_TARGETS:
        supported = ", ".join(SUPPORTED_TARGETS)
        raise ValueError(f"Unsupported default target: {default_target}. Supported targets: {supported}")
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"Output path is not a directory: {output_dir}")

    manifest = load_manifest(manifest_path)
    validated_manifest = validate_manifest(manifest, manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    warnings = []
    results = []
    for sample in validated_manifest["samples"]:
        result = _run_one_sample(
            sample=sample,
            manifest_target=validated_manifest.get("target"),
            output_dir=output_dir,
            default_target=default_target,
        )
        results.append(result)
        if result["error"] is not None and fail_fast:
            warnings.append("Validation stopped early because fail_fast is enabled.")
            break

    failed_samples = sum(1 for result in results if result["error"] is not None or not result["original_unchanged"])
    processed_samples = sum(1 for result in results if result["error"] is None)
    passed_samples = sum(1 for result in results if _result_passed(result))

    return {
        "action": "validate_samples",
        "manifest": str(manifest_path),
        "project": validated_manifest.get("project"),
        "output_dir": str(output_dir),
        "default_target": default_target,
        "total_samples": len(validated_manifest["samples"]),
        "processed_samples": processed_samples,
        "failed_samples": failed_samples,
        "passed_samples": passed_samples,
        "results": results,
        "summary": _summary(results),
        "warnings": warnings,
        "notes": [
            "Validation is local and does not commit audio.",
            "Validation outputs are technical reports, not legal clearance or platform certification.",
            "Validation does not evaluate or alter watermarks, fingerprints, detector signals, provenance markers, origin markers, C2PA markers, or attribution systems.",
            "Original input files are never modified by validation.",
        ],
    }


def _run_one_sample(sample: dict[str, Any], manifest_target: str | None, output_dir: Path, default_target: str) -> dict:
    sample_id = sample["id"]
    sample_path = Path(sample["resolved_path"])
    sample_target = sample.get("target") or manifest_target or default_target
    sample_presets = sample.get("presets")
    reported_presets = sample_presets if sample_presets is not None else list(DEFAULT_PRESETS)
    sample_output_dir = output_dir / _safe_label(sample_id)
    report_path = output_dir / f"{_safe_label(sample_id)}.validation.json"
    result = {
        "id": sample_id,
        "input": str(sample_path),
        "target": sample_target,
        "presets": reported_presets,
        "output_dir": str(sample_output_dir),
        "report": str(report_path),
        "doctor_passed": False,
        "doctor_score": None,
        "recommended_preset": None,
        "preset_eval_warning_count": 0,
        "original_unchanged": False,
        "error": None,
    }

    try:
        if not sample_path.exists():
            raise FileNotFoundError(f"Validation sample does not exist: {sample_path}")
        if not sample_path.is_file():
            raise ValueError(f"Validation sample path is not a file: {sample_path}")

        before_hash = sha256_file(sample_path)
        doctor = doctor_file(sample_path, target=sample_target)
        preset_report = preset_eval(sample_path, sample_output_dir, target=sample_target, presets=sample_presets)
        after_hash = sha256_file(sample_path)

        result.update(
            {
                "doctor_passed": bool(doctor.get("passed")),
                "doctor_score": doctor.get("score"),
                "recommended_preset": preset_report.get("recommended_preset"),
                "preset_eval_warning_count": _preset_warning_count(preset_report),
                "original_unchanged": before_hash == after_hash,
            }
        )
        write_json_report(
            {
                "action": "validate_sample",
                "result": result,
                "doctor": doctor,
                "preset_eval": preset_report,
            },
            report_path,
        )
    except Exception as exc:
        result["error"] = str(exc)
        write_json_report({"action": "validate_sample", "result": result}, report_path)

    return result


def _summary(results: list[dict]) -> dict:
    scores = [result["doctor_score"] for result in results if isinstance(result.get("doctor_score"), int)]
    return {
        "average_doctor_score": round(sum(scores) / len(scores), 2) if scores else None,
        "recommended_preset_counts": _recommended_preset_counts(results),
        "failed_ids": [
            result["id"]
            for result in results
            if result["error"] is not None or not result["original_unchanged"]
        ],
        "blocked_ids": [
            result["id"]
            for result in results
            if result["error"] is None and (not result["doctor_passed"] or result["recommended_preset"] is None)
        ],
        "warning_heavy_ids": [
            result["id"]
            for result in results
            if result["preset_eval_warning_count"] >= WARNING_HEAVY_THRESHOLD
        ],
        "best_candidates": [
            result["id"]
            for result in results
            if result["error"] is None
            and result["original_unchanged"]
            and result["recommended_preset"] is not None
            and (result["doctor_passed"] or (result["doctor_score"] or 0) >= HIGH_DOCTOR_SCORE)
        ],
    }


def _recommended_preset_counts(results: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        preset = result.get("recommended_preset")
        if preset is not None:
            counts[preset] = counts.get(preset, 0) + 1
    return counts


def _result_passed(result: dict) -> bool:
    return (
        result["error"] is None
        and result["original_unchanged"]
        and result["doctor_passed"]
        and result["recommended_preset"] is not None
    )


def _preset_warning_count(report: dict) -> int:
    warning_count = len(report.get("warnings", []))
    for result in report.get("results", []):
        warning_count += len(result.get("warnings", []))
    return warning_count


def _safe_label(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)
