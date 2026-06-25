"""Read-only audio comparison and regression checks."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from audio_quality_humanizer.analysis.audio_loader import load_audio
from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.analysis.release_check import SUPPORTED_TARGETS
from audio_quality_humanizer.metadata.cleaner import sha256_file


EPSILON = 1e-12
TARGET_PEAK_LIMITS = {
    "streaming": -1.0,
    "youtube": -1.0,
    "tunecore": -1.0,
    "club": -0.8,
}


SUMMARY_KEYS = (
    "path",
    "samplerate",
    "channels",
    "duration_seconds",
    "peak_dbfs",
    "rms_dbfs",
    "loudness_lufs_approx",
    "crest_factor_db",
    "clipping_sample_count",
    "leading_silence_ms",
    "trailing_silence_ms",
    "dynamic_range_estimate_db",
    "spectral_centroid_hz",
    "spectral_rolloff_95_hz",
    "low_band_energy_ratio_20_120_hz",
    "low_mid_mud_energy_ratio_180_450_hz",
    "harshness_energy_ratio_6000_12000_hz",
    "shimmer_band_energy_ratio_5000_8000_hz",
    "stereo_correlation",
    "side_energy_ratio",
    "low_end_stereo_warning",
    "mono_compatibility_warning",
    "warnings",
)


def compare_audio(reference_path: Path, candidate_path: Path, target: str = "streaming") -> dict:
    """Compare two audio files for technical quality regressions."""

    target = target.casefold()
    if target not in SUPPORTED_TARGETS:
        supported = ", ".join(SUPPORTED_TARGETS)
        raise ValueError(f"Unsupported compare target: {target}. Supported targets: {supported}")

    reference_path = Path(reference_path)
    candidate_path = Path(candidate_path)
    reference_analysis = analyze_audio(reference_path)
    candidate_analysis = analyze_audio(candidate_path)

    compatibility_warnings: list[str] = []
    compatibility = _compatibility(reference_analysis, candidate_analysis)
    if not compatibility["samplerate_match"]:
        compatibility_warnings.append("Sample rates differ, waveform-level comparison skipped.")
    if compatibility["samplerate_match"] and not compatibility["channels_match"]:
        compatibility_warnings.append("Channel counts differ, waveform comparison used mono downmix.")

    waveform_similarity = _waveform_similarity(
        reference_path,
        candidate_path,
        reference_analysis,
        candidate_analysis,
    )
    compatibility["comparable_sample_count"] = waveform_similarity["aligned_sample_count"]
    compatibility["compared_duration_seconds"] = waveform_similarity["compared_duration_seconds"]
    compatibility["comparison_method"] = waveform_similarity["comparison_method"]

    metric_deltas = _metric_deltas(reference_analysis, candidate_analysis)
    regressions = _detect_regressions(
        reference_analysis,
        candidate_analysis,
        metric_deltas,
        compatibility,
        target,
    )
    blocking_count = sum(1 for item in regressions if item["severity"] == "blocking")
    warning_count = sum(1 for item in regressions if item["severity"] == "warning")
    score = max(0, min(100, 100 - (25 * blocking_count) - (5 * warning_count)))
    warnings = _dedupe(compatibility_warnings + [item["message"] for item in regressions if item["severity"] == "warning"])
    recommendations = _recommendations(regressions, compatibility, target)

    return {
        "action": "compare",
        "target": target,
        "reference": _summary(reference_analysis),
        "candidate": _summary(candidate_analysis),
        "compatibility": compatibility,
        "metric_deltas": metric_deltas,
        "waveform_similarity": waveform_similarity,
        "regressions": regressions,
        "warnings": warnings,
        "recommendations": recommendations,
        "passed": blocking_count == 0,
        "score": score,
        "notes": [
            "Compare is read-only and does not alter audio.",
            "Compare evaluates audio quality and technical regression only.",
            "Compare does not evaluate or alter watermarks, fingerprints, provenance markers, origin markers, detector signals, or attribution systems.",
            "loudness_lufs_approx is RMS-based and not EBU/ITU compliant.",
        ],
    }


def _summary(analysis: dict) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in SUMMARY_KEYS:
        if key == "path":
            result[key] = analysis["file_info"]["path"]
        else:
            result[key] = analysis.get(key)
    return result


def _compatibility(reference: dict, candidate: dict) -> dict[str, Any]:
    duration_delta_ms = (candidate["duration_seconds"] - reference["duration_seconds"]) * 1000.0
    return {
        "samplerate_match": reference["samplerate"] == candidate["samplerate"],
        "channels_match": reference["channels"] == candidate["channels"],
        "duration_delta_ms": float(duration_delta_ms),
        "duration_match_within_100ms": abs(duration_delta_ms) <= 100.0,
        "comparable_sample_count": 0,
        "compared_duration_seconds": 0.0,
        "comparison_method": "pending",
    }


def _metric_deltas(reference: dict, candidate: dict) -> dict[str, float | int | None]:
    delta_pairs = {
        "peak_dbfs_delta": "peak_dbfs",
        "rms_dbfs_delta": "rms_dbfs",
        "loudness_lufs_approx_delta": "loudness_lufs_approx",
        "crest_factor_db_delta": "crest_factor_db",
        "dynamic_range_estimate_db_delta": "dynamic_range_estimate_db",
        "clipping_sample_count_delta": "clipping_sample_count",
        "near_clip_sample_count_delta": "near_clip_sample_count",
        "leading_silence_ms_delta": "leading_silence_ms",
        "trailing_silence_ms_delta": "trailing_silence_ms",
        "spectral_centroid_hz_delta": "spectral_centroid_hz",
        "spectral_rolloff_95_hz_delta": "spectral_rolloff_95_hz",
        "low_band_energy_ratio_delta": "low_band_energy_ratio_20_120_hz",
        "low_mid_mud_energy_ratio_delta": "low_mid_mud_energy_ratio_180_450_hz",
        "harshness_energy_ratio_delta": "harshness_energy_ratio_6000_12000_hz",
        "shimmer_band_energy_ratio_delta": "shimmer_band_energy_ratio_5000_8000_hz",
        "stereo_correlation_delta": "stereo_correlation",
        "side_energy_ratio_delta": "side_energy_ratio",
    }
    deltas: dict[str, float | int | None] = {}
    for delta_key, metric_key in delta_pairs.items():
        reference_value = reference.get(metric_key)
        candidate_value = candidate.get(metric_key)
        if reference_value is None or candidate_value is None:
            deltas[delta_key] = None
        else:
            delta = candidate_value - reference_value
            if isinstance(reference_value, int) and isinstance(candidate_value, int):
                deltas[delta_key] = int(delta)
            else:
                deltas[delta_key] = float(delta)
    return deltas


def _waveform_similarity(
    reference_path: Path,
    candidate_path: Path,
    reference_analysis: dict,
    candidate_analysis: dict,
) -> dict[str, Any]:
    reference_hash = sha256_file(reference_path)
    candidate_hash = sha256_file(candidate_path)
    identical_bytes = reference_hash == candidate_hash

    empty = {
        "aligned_sample_count": 0,
        "max_abs_difference": None,
        "mean_abs_difference": None,
        "rms_difference": None,
        "mono_correlation": None,
        "signal_to_difference_db": None,
        "identical_bytes": identical_bytes,
        "likely_identical_audio": identical_bytes,
        "compared_duration_seconds": 0.0,
        "comparison_method": "skipped_samplerate_mismatch",
    }
    if reference_analysis["samplerate"] != candidate_analysis["samplerate"]:
        return empty

    reference_audio = load_audio(reference_path)["audio"]
    candidate_audio = load_audio(candidate_path)["audio"]
    method = "same_channel_layout"
    if reference_audio.shape[1] != candidate_audio.shape[1]:
        reference_audio = np.mean(reference_audio, axis=1, keepdims=True)
        candidate_audio = np.mean(candidate_audio, axis=1, keepdims=True)
        method = "mono_downmix_channel_mismatch"

    shared_frames = min(reference_audio.shape[0], candidate_audio.shape[0])
    shared_channels = min(reference_audio.shape[1], candidate_audio.shape[1])
    if shared_frames <= 0 or shared_channels <= 0:
        empty["comparison_method"] = method
        return empty

    reference_aligned = reference_audio[:shared_frames, :shared_channels]
    candidate_aligned = candidate_audio[:shared_frames, :shared_channels]
    difference = candidate_aligned - reference_aligned
    abs_difference = np.abs(difference)
    rms_difference = float(np.sqrt(np.mean(np.square(difference))))
    reference_rms = float(np.sqrt(np.mean(np.square(reference_aligned))))
    mono_reference = np.mean(reference_aligned, axis=1)
    mono_candidate = np.mean(candidate_aligned, axis=1)
    mono_correlation = _correlation(mono_reference, mono_candidate)
    signal_to_difference_db = (
        float(20.0 * np.log10((reference_rms + EPSILON) / (rms_difference + EPSILON)))
        if rms_difference > 0.0
        else None
    )

    return {
        "aligned_sample_count": int(shared_frames * shared_channels),
        "max_abs_difference": float(np.max(abs_difference)),
        "mean_abs_difference": float(np.mean(abs_difference)),
        "rms_difference": rms_difference,
        "mono_correlation": mono_correlation,
        "signal_to_difference_db": signal_to_difference_db,
        "identical_bytes": identical_bytes,
        "likely_identical_audio": bool(rms_difference < 1e-9 or identical_bytes),
        "compared_duration_seconds": float(shared_frames / reference_analysis["samplerate"]),
        "comparison_method": method,
    }


def _detect_regressions(
    reference: dict,
    candidate: dict,
    deltas: dict,
    compatibility: dict,
    target: str,
) -> list[dict[str, str]]:
    regressions: list[dict[str, str]] = []
    target_peak_limit = TARGET_PEAK_LIMITS[target]

    if candidate["clipping_sample_count"] > 0 and reference["clipping_sample_count"] == 0:
        _add_regression(regressions, "blocking", "Candidate introduces clipping that was not present in the reference.")
    if deltas["clipping_sample_count_delta"] and deltas["clipping_sample_count_delta"] > 0:
        _add_regression(regressions, "blocking", "Candidate clipping sample count increased.")
    if candidate["peak_dbfs"] > target_peak_limit:
        _add_regression(regressions, "blocking", f"Candidate peak exceeds the {target} limit of {target_peak_limit} dBFS.")
    if not compatibility["duration_match_within_100ms"]:
        _add_regression(regressions, "blocking", "Candidate duration differs from reference by more than 100 ms.")
    if not compatibility["samplerate_match"]:
        _add_regression(regressions, "blocking", "Candidate sample rate differs from reference.")
    if candidate["rms_dbfs"] < -50.0:
        _add_regression(regressions, "blocking", "Candidate is almost silent.")
    if candidate["stereo_correlation"] is not None and candidate["stereo_correlation"] < -0.2:
        _add_regression(regressions, "blocking", "Candidate stereo correlation becomes strongly negative.")
    if target == "club" and candidate["low_end_stereo_warning"] and not reference["low_end_stereo_warning"]:
        _add_regression(regressions, "blocking", "Candidate introduces low-end stereo risk for club target.")

    _warning_if_abs_exceeds(regressions, deltas, "loudness_lufs_approx_delta", 3.0, "Candidate loudness changes by more than 3 dB.")
    _warning_if_abs_exceeds(regressions, deltas, "rms_dbfs_delta", 3.0, "Candidate RMS level changes by more than 3 dB.")
    if deltas["crest_factor_db_delta"] is not None and deltas["crest_factor_db_delta"] < -3.0:
        _add_regression(regressions, "warning", "Candidate crest factor drops by more than 3 dB.")
    if (
        deltas["dynamic_range_estimate_db_delta"] is not None
        and deltas["dynamic_range_estimate_db_delta"] < -4.0
    ):
        _add_regression(regressions, "warning", "Candidate dynamic range estimate drops by more than 4 dB.")
    if deltas["harshness_energy_ratio_delta"] is not None and deltas["harshness_energy_ratio_delta"] > 0.08:
        _add_regression(regressions, "warning", "Candidate harshness-band energy ratio increases strongly.")
    if deltas["low_mid_mud_energy_ratio_delta"] is not None and deltas["low_mid_mud_energy_ratio_delta"] > 0.10:
        _add_regression(regressions, "warning", "Candidate low-mid mud energy ratio increases strongly.")
    if deltas["shimmer_band_energy_ratio_delta"] is not None and deltas["shimmer_band_energy_ratio_delta"] > 0.08:
        _add_regression(regressions, "warning", "Candidate shimmer-band energy ratio increases strongly.")
    _warning_if_abs_exceeds(regressions, deltas, "side_energy_ratio_delta", 0.5, "Candidate side energy changes strongly.")
    if deltas["leading_silence_ms_delta"] is not None and deltas["leading_silence_ms_delta"] > 1000.0:
        _add_regression(regressions, "warning", "Candidate leading silence increases by more than 1000 ms.")
    if deltas["trailing_silence_ms_delta"] is not None and deltas["trailing_silence_ms_delta"] > 1000.0:
        _add_regression(regressions, "warning", "Candidate trailing silence increases by more than 1000 ms.")

    return regressions


def _recommendations(regressions: list[dict[str, str]], compatibility: dict, target: str) -> list[str]:
    recommendations = []
    if regressions:
        recommendations.append("Review blocking and warning regressions before accepting the candidate.")
    if not compatibility["samplerate_match"]:
        recommendations.append("Render reference and candidate at the same sample rate for waveform-level comparison.")
    if not compatibility["duration_match_within_100ms"]:
        recommendations.append("Confirm that duration differences are intentional.")
    if target == "club":
        recommendations.append("For club targets, review low-end mono compatibility and transient impact.")
    if not recommendations:
        recommendations.append("No technical regression recommendations from this compare run.")
    return _dedupe(recommendations)


def _warning_if_abs_exceeds(
    regressions: list[dict[str, str]],
    deltas: dict,
    key: str,
    threshold: float,
    message: str,
) -> None:
    if deltas[key] is not None and abs(deltas[key]) > threshold:
        _add_regression(regressions, "warning", message)


def _add_regression(regressions: list[dict[str, str]], severity: str, message: str) -> None:
    item = {"severity": severity, "message": message}
    if item not in regressions:
        regressions.append(item)


def _correlation(reference: np.ndarray, candidate: np.ndarray) -> float | None:
    if reference.size < 2 or candidate.size < 2:
        return None
    reference_std = float(np.std(reference))
    candidate_std = float(np.std(candidate))
    if reference_std <= EPSILON or candidate_std <= EPSILON:
        return 1.0 if np.allclose(reference, candidate, atol=1e-12) else None
    return float(np.corrcoef(reference, candidate)[0, 1])


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
