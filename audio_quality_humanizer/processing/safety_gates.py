"""Safety gates for conservative processing output."""

from __future__ import annotations


TARGET_PEAK_LIMITS = {
    "streaming": -1.0,
    "youtube": -1.0,
    "tunecore": -1.0,
    "club": -0.8,
}


def evaluate_processing_safety(before: dict, after: dict, comparison: dict, preset: str, target: str) -> dict:
    """Evaluate whether processed output remains within conservative limits."""

    blocking_issues: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []
    preset = preset.casefold()
    target = target.casefold()

    if not _has_required_metrics(after):
        blocking_issues.append("Output file is missing, unreadable, or missing required analysis metrics.")
        return _result(blocking_issues, warnings, recommendations)

    deltas = comparison.get("metric_deltas", {})
    compatibility = comparison.get("compatibility", {})

    if after["clipping_sample_count"] > 0:
        blocking_issues.append("Output has clipping.")
    target_limit = TARGET_PEAK_LIMITS.get(target, -1.0)
    if after["peak_dbfs"] > target_limit + 0.1:
        blocking_issues.append("Output peak exceeds target ceiling by more than 0.1 dB.")
    if after["rms_dbfs"] < -70.0:
        blocking_issues.append("Output became almost silent.")

    rms_delta = _delta(before, after, "rms_dbfs", deltas.get("rms_dbfs_delta"))
    if abs(rms_delta) > 1.5:
        blocking_issues.append("RMS changed by more than 1.5 dB.")
    if preset == "subtle" and abs(rms_delta) > 0.5:
        blocking_issues.append("Subtle preset RMS changed by more than 0.5 dB.")

    crest_delta = _delta(before, after, "crest_factor_db", deltas.get("crest_factor_db_delta"))
    if crest_delta < -1.5:
        blocking_issues.append("Crest factor dropped by more than 1.5 dB.")
    if preset == "afro-club" and crest_delta < -1.0:
        blocking_issues.append("Afro-club preset crest factor dropped by more than 1.0 dB.")
    if preset in {"club", "afro-club"} and after["crest_factor_db"] < 8.0:
        blocking_issues.append("Crest factor is below 8.0 dB for club-oriented preset.")

    if abs(float(compatibility.get("duration_delta_ms", 0.0))) > 10.0:
        blocking_issues.append("Duration changed by more than 10 ms.")
    if compatibility.get("samplerate_match") is False or before.get("samplerate") != after.get("samplerate"):
        blocking_issues.append("Sample rate changed.")
    if compatibility.get("channels_match") is False or before.get("channels") != after.get("channels"):
        blocking_issues.append("Channel count changed.")

    after_corr = after.get("stereo_correlation")
    before_corr = before.get("stereo_correlation")
    if after_corr is not None and after_corr < -0.2:
        blocking_issues.append("Stereo correlation became strongly negative.")
    if before_corr is not None and after_corr is not None and before_corr - after_corr > 0.2 and after_corr < 0.3:
        blocking_issues.append("Stereo correlation dropped by more than 0.2 and final correlation is below 0.3.")

    if preset in {"club", "afro-club"} and after.get("low_end_stereo_warning") and not before.get("low_end_stereo_warning"):
        blocking_issues.append("Club-oriented preset introduced low-end stereo warning.")

    if comparison.get("passed") is False:
        blocking_issues.append("Compare reported blocking regressions.")

    _add_warning_if_positive_delta(
        warnings,
        deltas,
        "harshness_energy_ratio_delta",
        0.0,
        "Harshness increased.",
    )
    _add_warning_if_positive_delta(warnings, deltas, "low_mid_mud_energy_ratio_delta", 0.0, "Mud increased.")
    _add_warning_if_positive_delta(
        warnings,
        deltas,
        "shimmer_band_energy_ratio_delta",
        0.05,
        "Shimmer increased strongly.",
    )
    if _delta(before, after, "dynamic_range_estimate_db", deltas.get("dynamic_range_estimate_db_delta")) < -3.0:
        warnings.append("Dynamic range dropped by more than 3 dB.")
    if crest_delta < -0.75:
        warnings.append("Crest factor dropped by more than 0.75 dB.")
    if abs(float(deltas.get("side_energy_ratio_delta") or 0.0)) > 0.5:
        warnings.append("Side energy changed strongly.")
    if (deltas.get("near_clip_sample_count_delta") or 0) > 0:
        warnings.append("Near-clip sample count increased.")
    if abs(_delta(before, after, "loudness_lufs_approx", deltas.get("loudness_lufs_approx_delta"))) > 1.0:
        warnings.append("Approximate loudness changed by more than 1.0 dB.")
    if preset in {"club", "afro-club"} and abs(float(deltas.get("low_band_energy_ratio_delta") or 0.0)) > 0.10:
        warnings.append("Low-end energy changed strongly for club-oriented preset.")

    if blocking_issues:
        recommendations.append("Use a subtler preset or inspect the source and rendered output manually.")
    if warnings:
        recommendations.append("Review warning-level metric changes before accepting the output.")
    if not blocking_issues and not warnings:
        recommendations.append("Processing remained within conservative safety gates.")

    return _result(blocking_issues, warnings, recommendations)


def _has_required_metrics(report: dict) -> bool:
    required = ["clipping_sample_count", "peak_dbfs", "rms_dbfs", "crest_factor_db", "samplerate", "channels"]
    return isinstance(report, dict) and all(key in report for key in required)


def _delta(before: dict, after: dict, key: str, reported_delta) -> float:
    if reported_delta is not None:
        return float(reported_delta)
    return float(after.get(key, 0.0) - before.get(key, 0.0))


def _add_warning_if_positive_delta(
    warnings: list[str],
    deltas: dict,
    key: str,
    threshold: float,
    message: str,
) -> None:
    if float(deltas.get(key) or 0.0) > threshold:
        warnings.append(message)


def _result(blocking_issues: list[str], warnings: list[str], recommendations: list[str]) -> dict:
    return {
        "passed": not blocking_issues,
        "blocking_issues": _dedupe(blocking_issues),
        "warnings": _dedupe(warnings),
        "recommendations": _dedupe(recommendations),
    }


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
