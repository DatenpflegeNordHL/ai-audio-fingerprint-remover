"""Release-readiness preflight checks."""

from __future__ import annotations

from pathlib import Path

from audio_quality_humanizer.analysis.metrics import analyze_audio


SUPPORTED_TARGETS = ("streaming", "youtube", "club", "tunecore")


def release_check(path: Path, target: str = "streaming") -> dict:
    """Run pragmatic technical release-readiness checks."""

    target = target.casefold()
    if target not in SUPPORTED_TARGETS:
        supported = ", ".join(SUPPORTED_TARGETS)
        raise ValueError(f"Unsupported release-check target: {target}. Supported targets: {supported}")

    analysis = analyze_audio(path)
    blocking_issues: list[str] = []
    warnings = list(analysis["warnings"])
    recommendations = [
        "Use these checks as a technical preflight, not as official distributor or platform certification."
    ]

    if analysis["clipping_sample_count"] > 0:
        blocking_issues.append("Clipping samples must be fixed before release.")

    if target in {"streaming", "youtube", "tunecore"}:
        _streaming_like_checks(analysis, warnings, recommendations, blocking_issues, target)
    elif target == "club":
        _club_checks(analysis, warnings, recommendations, blocking_issues)

    score = _score_report(blocking_issues, warnings)

    return {
        "action": "release_check",
        "target": target,
        "passed": not blocking_issues,
        "score": score,
        "blocking_issues": blocking_issues,
        "warnings": _dedupe(warnings),
        "recommendations": _dedupe(recommendations),
        "analysis": analysis,
        "notes": [
            "Release-check is a pragmatic technical preflight and not official platform certification.",
            "loudness_lufs_approx is RMS-based and not EBU/ITU compliant LUFS.",
            "Release-check is read-only and does not alter audio files.",
        ],
    }


def _streaming_like_checks(
    analysis: dict,
    warnings: list[str],
    recommendations: list[str],
    blocking_issues: list[str],
    target: str,
) -> None:
    if analysis["peak_dbfs"] > -1.0:
        warnings.append(f"{target} target usually expects peak level at or below -1.0 dBFS.")
        recommendations.append("Lower the final peak ceiling to leave delivery headroom.")
    if not -14.0 <= analysis["loudness_lufs_approx"] <= -9.0:
        message = f"{target} target usually expects approximate loudness between -14 and -9 LUFS."
        if target == "tunecore" and (
            analysis["loudness_lufs_approx"] > -7.0 or analysis["loudness_lufs_approx"] < -20.0
        ):
            blocking_issues.append("Severe loudness issue for conservative distribution preflight.")
        warnings.append(message)
        recommendations.append("Review integrated loudness with a standards-compliant meter before delivery.")
    if analysis["stereo_correlation"] is not None and analysis["stereo_correlation"] < -0.2:
        if target == "tunecore":
            blocking_issues.append("Severe stereo/phase issue for conservative distribution preflight.")
        warnings.append("Stereo correlation is strongly negative.")
        recommendations.append("Review mono compatibility before release.")
    if analysis["leading_silence_ms"] > 3000.0 or analysis["trailing_silence_ms"] > 5000.0:
        if target == "tunecore":
            blocking_issues.append("Broken silence boundaries for conservative distribution preflight.")
        warnings.append("Excessive silence may affect release presentation.")
        recommendations.append("Trim unintended leading or trailing silence.")


def _club_checks(
    analysis: dict,
    warnings: list[str],
    recommendations: list[str],
    blocking_issues: list[str],
) -> None:
    recommendations.append("Check low-end mono compatibility for club playback systems.")
    if analysis["peak_dbfs"] > -0.8:
        warnings.append("Club target usually expects peak level at or below -0.8 dBFS.")
        recommendations.append("Leave a little more true-peak headroom before playback conversion.")
    if not -10.0 <= analysis["loudness_lufs_approx"] <= -7.0:
        warnings.append("Club target is often louder, roughly -10 to -7 LUFS approximate.")
        recommendations.append("Confirm loudness against the intended playback context.")
    if analysis["low_end_stereo_warning"]:
        warnings.append("Low-end stereo risk is important for club playback.")
        recommendations.append("Review bass content for mono compatibility.")
    if analysis["crest_factor_db"] < 6.0:
        warnings.append("Crest factor is very low for club playback.")
        recommendations.append("Review whether compression is flattening transient impact.")
    if analysis["overcompression_warning"]:
        warnings.append("Strong overcompression warning for club target.")


def _score_report(blocking_issues: list[str], warnings: list[str]) -> int:
    score = 100 - (35 * len(blocking_issues)) - (5 * len(_dedupe(warnings)))
    return max(0, min(100, int(score)))


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
