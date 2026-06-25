"""Signal guardrails for conservative audio-quality workflows."""

from __future__ import annotations

from typing import Any

import numpy as np


EPSILON = 1e-12
MIN_REASONABLE_SAMPLERATE = 8_000
MAX_REASONABLE_SAMPLERATE = 384_000


def validate_audio_array(audio: Any, *, allow_empty: bool = False) -> dict:
    """Validate an audio-like array without changing it."""

    array = np.asarray(audio)
    shape = _shape_list(array)
    numeric = bool(np.issubdtype(array.dtype, np.number))
    empty = bool(array.size == 0)
    warnings: list[str] = []

    nan_count = 0
    inf_count = 0
    peak = 0.0
    silent = False
    if numeric:
        numeric_array = np.asarray(array, dtype=np.float64)
        nan_count = int(np.count_nonzero(np.isnan(numeric_array)))
        inf_count = int(np.count_nonzero(np.isinf(numeric_array)))
        finite = numeric_array[np.isfinite(numeric_array)]
        peak = float(np.max(np.abs(finite))) if finite.size else 0.0
        silent = bool((not empty) and finite.size == array.size and peak <= EPSILON)
    else:
        warnings.append("Audio array must contain numeric values.")

    if empty and not allow_empty:
        warnings.append("Audio array is empty.")
    if nan_count:
        warnings.append("NaN values were detected.")
    if inf_count:
        warnings.append("Infinite values were detected.")
    if silent:
        warnings.append("Audio array is silent.")
    if peak > 1.0:
        warnings.append("Peak level is above full scale.")
    if array.ndim > 2:
        warnings.append("Audio array has more than two dimensions.")

    valid = bool(
        numeric
        and (allow_empty or not empty)
        and nan_count == 0
        and inf_count == 0
        and peak <= 1.0
        and array.ndim <= 2
    )

    return {
        "valid": valid,
        "numeric": numeric,
        "empty": empty,
        "dtype": str(array.dtype),
        "shape": shape,
        "ndim": int(array.ndim),
        "sample_count": int(array.size),
        "frame_count": _frame_count(array),
        "channel_count": _channel_count(array),
        "nan_count": nan_count,
        "inf_count": inf_count,
        "silent": silent,
        "peak": peak,
        "peak_above_full_scale": bool(peak > 1.0),
        "warnings": warnings,
        "actions": [],
    }


def sanitize_audio_array(audio: Any) -> tuple[np.ndarray, dict]:
    """Replace NaN and infinite values with silence without normalizing audio."""

    array = np.asarray(audio)
    before = validate_audio_array(array, allow_empty=True)
    actions: list[str] = []
    warnings = list(before["warnings"])

    if not before["numeric"]:
        warnings.append("Sanitization skipped because the array is non-numeric.")
        return array.copy(), {
            "changed": False,
            "input_valid": before["valid"],
            "output_valid": before["valid"],
            "nan_count_before": before["nan_count"],
            "inf_count_before": before["inf_count"],
            "nan_count_after": before["nan_count"],
            "inf_count_after": before["inf_count"],
            "shape_before": before["shape"],
            "shape_after": before["shape"],
            "actions": actions,
            "warnings": warnings,
        }

    sanitized = np.asarray(array, dtype=np.float64).copy()
    nonfinite_mask = ~np.isfinite(sanitized)
    changed = bool(np.any(nonfinite_mask))
    if changed:
        sanitized[nonfinite_mask] = 0.0
        actions.append("Replaced NaN and infinite values with 0.0.")

    after = validate_audio_array(sanitized, allow_empty=True)
    return sanitized, {
        "changed": changed,
        "input_valid": before["valid"],
        "output_valid": after["valid"],
        "nan_count_before": before["nan_count"],
        "inf_count_before": before["inf_count"],
        "nan_count_after": after["nan_count"],
        "inf_count_after": after["inf_count"],
        "shape_before": before["shape"],
        "shape_after": after["shape"],
        "actions": actions,
        "warnings": _dedupe(warnings + after["warnings"]),
    }


def validate_samplerate(samplerate: Any) -> dict:
    """Validate a sample rate for ordinary audio workflow reporting."""

    warnings: list[str] = []
    value: int | None = None
    numeric = isinstance(samplerate, (int, float, np.integer, np.floating)) and not isinstance(samplerate, bool)
    finite = bool(numeric and np.isfinite(samplerate))
    integer_like = bool(finite and float(samplerate).is_integer())
    if finite:
        value = int(samplerate)

    if not numeric:
        warnings.append("Sample rate must be numeric.")
    elif not finite:
        warnings.append("Sample rate must be finite.")
    elif not integer_like:
        warnings.append("Sample rate should be an integer value.")
    elif value is not None and value <= 0:
        warnings.append("Sample rate must be positive.")
    elif value is not None and value < MIN_REASONABLE_SAMPLERATE:
        warnings.append("Sample rate is below the supported workflow range.")
    elif value is not None and value > MAX_REASONABLE_SAMPLERATE:
        warnings.append("Sample rate is above the supported workflow range.")

    valid = bool(
        integer_like
        and value is not None
        and MIN_REASONABLE_SAMPLERATE <= value <= MAX_REASONABLE_SAMPLERATE
    )

    return {
        "valid": valid,
        "samplerate": value,
        "numeric": bool(numeric),
        "integer_like": integer_like,
        "warnings": warnings,
        "actions": [],
    }


def validate_processing_result(before: Any, after: Any, *, max_peak_allowed: float = 1.0) -> dict:
    """Validate that processed output preserves core array properties."""

    before_report = validate_audio_array(before)
    after_report = validate_audio_array(after)
    shape_changed = before_report["shape"] != after_report["shape"]
    length_changed = before_report["frame_count"] != after_report["frame_count"]
    channel_count_changed = before_report["channel_count"] != after_report["channel_count"]
    peak_above_allowed = bool(after_report["peak"] > float(max_peak_allowed))

    warnings = list(before_report["warnings"]) + list(after_report["warnings"])
    if shape_changed:
        warnings.append("Output shape differs from input shape.")
    if length_changed:
        warnings.append("Output length differs from input length.")
    if channel_count_changed:
        warnings.append("Output channel count differs from input channel count.")
    if peak_above_allowed:
        warnings.append("Output peak is above the configured safe threshold.")

    valid = bool(
        before_report["valid"]
        and after_report["valid"]
        and not shape_changed
        and not length_changed
        and not channel_count_changed
        and not peak_above_allowed
    )

    return {
        "valid": valid,
        "input_valid": before_report["valid"],
        "output_valid": after_report["valid"],
        "shape_before": before_report["shape"],
        "shape_after": after_report["shape"],
        "shape_changed": shape_changed,
        "length_changed": length_changed,
        "channel_count_changed": channel_count_changed,
        "peak_after": after_report["peak"],
        "max_peak_allowed": float(max_peak_allowed),
        "peak_above_allowed": peak_above_allowed,
        "warnings": _dedupe(warnings),
        "actions": [],
    }


def calculate_signal_guardrail_report(before: Any, after: Any | None = None, samplerate: Any | None = None) -> dict:
    """Build a JSON-safe signal guardrail report."""

    before_report = validate_audio_array(before)
    after_report = validate_audio_array(after) if after is not None else None
    samplerate_report = validate_samplerate(samplerate) if samplerate is not None else None
    processing_report = validate_processing_result(before, after) if after is not None else None

    warnings = list(before_report["warnings"])
    actions: list[str] = []
    if after_report is not None:
        warnings.extend(after_report["warnings"])
    if samplerate_report is not None:
        warnings.extend(samplerate_report["warnings"])
    if processing_report is not None:
        warnings.extend(processing_report["warnings"])
        actions.extend(processing_report["actions"])

    guardrails = {
        "input_valid": before_report["valid"],
        "output_valid": after_report["valid"] if after_report is not None else None,
        "nan_count_before": before_report["nan_count"],
        "inf_count_before": before_report["inf_count"],
        "nan_count_after": after_report["nan_count"] if after_report is not None else 0,
        "inf_count_after": after_report["inf_count"] if after_report is not None else 0,
        "shape_before": before_report["shape"],
        "shape_after": after_report["shape"] if after_report is not None else [],
        "samplerate": samplerate_report["samplerate"] if samplerate_report is not None else None,
        "samplerate_valid": samplerate_report["valid"] if samplerate_report is not None else None,
        "input_silent": before_report["silent"],
        "output_silent": after_report["silent"] if after_report is not None else None,
        "peak_before": before_report["peak"],
        "peak_after": after_report["peak"] if after_report is not None else None,
        "shape_changed": processing_report["shape_changed"] if processing_report is not None else False,
        "length_changed": processing_report["length_changed"] if processing_report is not None else False,
        "channel_count_changed": (
            processing_report["channel_count_changed"] if processing_report is not None else False
        ),
        "warnings": _dedupe(warnings),
        "actions": _dedupe(actions),
    }
    return {"guardrails": guardrails}


def _shape_list(array: np.ndarray) -> list[int]:
    return [int(value) for value in array.shape]


def _frame_count(array: np.ndarray) -> int:
    if array.ndim == 0:
        return int(array.size)
    return int(array.shape[0]) if array.size else 0


def _channel_count(array: np.ndarray) -> int:
    if array.ndim <= 1:
        return 1 if array.size else 0
    return int(array.shape[1])


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
