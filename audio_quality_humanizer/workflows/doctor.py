"""Read-only one-file workflow preflight."""

from __future__ import annotations

from pathlib import Path

from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.analysis.release_check import release_check
from audio_quality_humanizer.metadata.cleaner import inspect_metadata, inspect_provenance


def doctor_file(input_path: Path, target: str = "streaming") -> dict:
    """Run metadata, provenance, analysis, and release preflight checks."""

    input_path = Path(input_path)
    metadata = inspect_metadata(input_path)
    provenance = inspect_provenance(input_path)
    analysis = analyze_audio(input_path)
    release = release_check(input_path, target=target)

    possible_provenance_keys = provenance.get("possible_provenance_keys", [])
    metadata_read_error = metadata.get("metadata", {}).get("metadata_read_error")
    score = int(release.get("score", 0))
    if possible_provenance_keys:
        score -= 5
    if metadata_read_error:
        score -= 5
    score = max(0, min(100, score))

    warnings = _dedupe(
        metadata.get("warnings", [])
        + provenance.get("warnings", [])
        + analysis.get("warnings", [])
        + release.get("warnings", [])
    )
    recommendations = list(release.get("recommendations", []))
    ordinary_metadata_keys = metadata.get("metadata", {}).get("ordinary_metadata_keys", [])
    if ordinary_metadata_keys:
        recommendations.append("Run clean-metadata on a copy if you want to remove ordinary user-editable tags.")
    if possible_provenance_keys:
        recommendations.append(
            "Review possible provenance-related metadata manually. Do not remove provenance-related metadata silently."
        )

    return {
        "action": "doctor",
        "target": target,
        "input": str(input_path),
        "passed": bool(release.get("passed", False)),
        "score": score,
        "metadata": metadata,
        "provenance": provenance,
        "analysis": analysis,
        "release_check": release,
        "blocking_issues": release.get("blocking_issues", []),
        "warnings": warnings,
        "recommendations": _dedupe(recommendations),
        "notes": [
            "Doctor is read-only.",
            "Doctor is a technical audio quality and metadata preflight.",
            "Doctor is not official distributor/platform certification.",
            "Doctor does not evaluate or alter watermarks, fingerprints, detector signals, provenance markers, origin markers, C2PA markers, or attribution systems.",
        ],
    }


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
