"""Read-only visualization artifact generation for audio reports."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from audio_quality_humanizer.analysis.audio_loader import load_audio
from audio_quality_humanizer.analysis.compare import compare_audio
from audio_quality_humanizer.analysis.metrics import analyze_audio


SCHEMA_VERSION = "1.0"
SAFETY_NOTE = (
    "Visualization artifacts show measured technical audio features only. "
    "They do not evaluate or remove watermarks, fingerprints, provenance, C2PA markers, "
    "source-attribution markers, detector signals, or platform acceptance."
)
EPSILON = 1e-12
MIN_DB = -120.0
DEFAULT_MAX_TIME_BINS = 256
DEFAULT_MAX_FREQUENCY_BINS = 128
DEFAULT_MAX_WAVEFORM_WINDOWS = 512
DEFAULT_DELTA_THRESHOLD_DB = 1.0
ALLOWED_TOOLTIP_LABELS = {
    "clipping reduced",
    "peak changed",
    "RMS changed",
    "dynamic range changed",
    "spectral centroid changed",
    "spectral rolloff changed",
    "stereo correlation changed",
    "side energy changed",
    "spectral energy changed",
    "metadata changed",
}


def build_visualization_artifacts(
    input_path: Path,
    *,
    max_time_bins: int = DEFAULT_MAX_TIME_BINS,
    max_frequency_bins: int = DEFAULT_MAX_FREQUENCY_BINS,
    max_waveform_windows: int = DEFAULT_MAX_WAVEFORM_WINDOWS,
) -> dict[str, Any]:
    """Build read-only single-file visualization artifacts."""

    input_path = Path(input_path)
    loaded = load_audio(input_path)
    analysis = analyze_audio(input_path)
    audio = loaded["audio"]
    samplerate = loaded["samplerate"]

    report = {
        "action": "visualize",
        "schema_version": SCHEMA_VERSION,
        "source": _source_summary(loaded),
        "waveform_peaks": _waveform_peaks(audio, samplerate, max_waveform_windows),
        "spectrogram": _spectrogram_artifact(audio, samplerate, max_time_bins, max_frequency_bins),
        "metric_cards": _metric_cards(analysis),
        "tooltip_regions": _single_file_tooltip_regions(analysis),
        "safety_notes": [SAFETY_NOTE],
    }
    return _json_safe_value(report)


def build_visualization_comparison(
    reference_path: Path,
    candidate_path: Path,
    *,
    target: str = "streaming",
    max_time_bins: int = DEFAULT_MAX_TIME_BINS,
    max_frequency_bins: int = DEFAULT_MAX_FREQUENCY_BINS,
    max_waveform_windows: int = DEFAULT_MAX_WAVEFORM_WINDOWS,
) -> dict[str, Any]:
    """Build read-only before/after visualization comparison artifacts."""

    reference_path = Path(reference_path)
    candidate_path = Path(candidate_path)
    reference_loaded = load_audio(reference_path)
    candidate_loaded = load_audio(candidate_path)
    comparison = compare_audio(reference_path, candidate_path, target)

    reference_artifact = {
        "source": _source_summary(reference_loaded),
        "waveform_peaks": _waveform_peaks(
            reference_loaded["audio"],
            reference_loaded["samplerate"],
            max_waveform_windows,
        ),
        "spectrogram": _spectrogram_artifact(
            reference_loaded["audio"],
            reference_loaded["samplerate"],
            max_time_bins,
            max_frequency_bins,
        ),
        "metric_cards": _metric_cards_from_summary(comparison["reference"]),
    }
    candidate_artifact = {
        "source": _source_summary(candidate_loaded),
        "waveform_peaks": _waveform_peaks(
            candidate_loaded["audio"],
            candidate_loaded["samplerate"],
            max_waveform_windows,
        ),
        "spectrogram": _spectrogram_artifact(
            candidate_loaded["audio"],
            candidate_loaded["samplerate"],
            max_time_bins,
            max_frequency_bins,
        ),
        "metric_cards": _metric_cards_from_summary(comparison["candidate"]),
    }
    difference_map = _difference_map(
        reference_loaded,
        candidate_loaded,
        max_time_bins,
        max_frequency_bins,
    )

    report = {
        "action": "visualize-compare",
        "schema_version": SCHEMA_VERSION,
        "target": target,
        "reference": reference_artifact,
        "candidate": candidate_artifact,
        "comparison_metrics": comparison["comparison_metrics"],
        "compatibility": comparison["compatibility"],
        "difference_map": difference_map,
        "tooltip_regions": _comparison_tooltip_regions(comparison, difference_map),
        "safety_notes": [SAFETY_NOTE],
    }
    return _json_safe_value(report)


def _source_summary(loaded: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": loaded["path"],
        "duration_seconds": loaded["duration_seconds"],
        "sample_rate": loaded["samplerate"],
        "channels": loaded["channels"],
        "frames": loaded["frames"],
        "format": loaded["format"],
        "subtype": loaded["subtype"],
    }


def _waveform_peaks(
    audio: np.ndarray,
    samplerate: int,
    max_windows: int,
) -> dict[str, Any]:
    frames = int(audio.shape[0])
    max_windows = max(1, int(max_windows))
    if frames <= 0:
        return {
            "sample_count": 0,
            "window_count": 0,
            "window_size_samples": 0,
            "peaks": [],
        }

    window_count = min(max_windows, frames)
    window_size = max(1, int(np.ceil(frames / window_count)))
    peaks: list[dict[str, float]] = []
    for start in range(0, frames, window_size):
        if len(peaks) >= max_windows:
            break
        end = min(start + window_size, frames)
        segment = audio[start:end]
        if segment.size == 0:
            continue
        peaks.append(
            {
                "time_start_seconds": float(start / samplerate) if samplerate > 0 else 0.0,
                "time_end_seconds": float(end / samplerate) if samplerate > 0 else 0.0,
                "min": float(np.min(segment)),
                "max": float(np.max(segment)),
                "abs_peak": float(np.max(np.abs(segment))),
            }
        )
    return {
        "sample_count": int(frames * int(audio.shape[1])),
        "window_count": len(peaks),
        "window_size_samples": int(window_size),
        "peaks": peaks,
    }


def _spectrogram_artifact(
    audio: np.ndarray,
    samplerate: int,
    max_time_bins: int,
    max_frequency_bins: int,
) -> dict[str, Any]:
    spectrogram = _spectrogram_matrix(audio, samplerate, max_time_bins, max_frequency_bins)
    energy = spectrogram["energy_db"]
    if energy.size:
        summary = {
            "min_energy_db": float(np.min(energy)),
            "max_energy_db": float(np.max(energy)),
            "mean_energy_db": float(np.mean(energy)),
            "time_bin_count": int(energy.shape[0]),
            "frequency_bin_count": int(energy.shape[1]),
            "energy_floor_db": MIN_DB,
            "official_standard": False,
        }
    else:
        summary = {
            "min_energy_db": MIN_DB,
            "max_energy_db": MIN_DB,
            "mean_energy_db": MIN_DB,
            "time_bin_count": 0,
            "frequency_bin_count": 0,
            "energy_floor_db": MIN_DB,
            "official_standard": False,
        }
    return {
        "time_bins": spectrogram["time_bins"].tolist(),
        "frequency_bins_hz": spectrogram["frequency_bins_hz"].tolist(),
        "energy_db": energy.tolist(),
        "summary": summary,
    }


def _spectrogram_matrix(
    audio: np.ndarray,
    samplerate: int,
    max_time_bins: int,
    max_frequency_bins: int,
) -> dict[str, np.ndarray]:
    max_time_bins = max(1, int(max_time_bins))
    max_frequency_bins = max(1, int(max_frequency_bins))
    frames = int(audio.shape[0])
    if frames <= 0 or samplerate <= 0:
        return {
            "time_bins": np.asarray([], dtype=np.float64),
            "frequency_bins_hz": np.asarray([], dtype=np.float64),
            "energy_db": np.zeros((0, 0), dtype=np.float64),
        }

    mono = np.mean(audio, axis=1)
    time_bin_count = min(max_time_bins, frames)
    window_size = max(1, int(np.ceil(frames / time_bin_count)))
    fft_size = max(2, _next_power_of_two(window_size))
    raw_energy_rows: list[np.ndarray] = []
    time_bins: list[float] = []
    for start in range(0, frames, window_size):
        if len(raw_energy_rows) >= max_time_bins:
            break
        end = min(start + window_size, frames)
        segment = mono[start:end]
        if segment.size == 0:
            continue
        if segment.size < fft_size:
            segment = np.pad(segment, (0, fft_size - segment.size))
        windowed = segment[:fft_size] * np.hanning(fft_size)
        magnitude = np.abs(np.fft.rfft(windowed))
        power = np.square(magnitude)
        raw_energy_rows.append(power)
        time_bins.append(float(((start + end) * 0.5) / samplerate))

    if not raw_energy_rows:
        return {
            "time_bins": np.asarray([], dtype=np.float64),
            "frequency_bins_hz": np.asarray([], dtype=np.float64),
            "energy_db": np.zeros((0, 0), dtype=np.float64),
        }

    raw_energy = np.vstack(raw_energy_rows)
    raw_freqs = np.fft.rfftfreq(fft_size, d=1.0 / samplerate)
    freq_count = min(max_frequency_bins, raw_energy.shape[1])
    edges = np.linspace(0, raw_energy.shape[1], freq_count + 1, dtype=int)
    energy_columns: list[np.ndarray] = []
    frequency_bins: list[float] = []
    for index in range(freq_count):
        start = int(edges[index])
        end = int(edges[index + 1])
        if end <= start:
            end = min(start + 1, raw_energy.shape[1])
        bucket = raw_energy[:, start:end]
        energy_columns.append(np.mean(bucket, axis=1))
        frequency_bins.append(float(np.mean(raw_freqs[start:end])))
    energy = np.column_stack(energy_columns)
    energy_db = 10.0 * np.log10(np.maximum(energy, EPSILON))
    energy_db = np.maximum(energy_db, MIN_DB)
    return {
        "time_bins": np.asarray(time_bins, dtype=np.float64),
        "frequency_bins_hz": np.asarray(frequency_bins, dtype=np.float64),
        "energy_db": energy_db.astype(np.float64),
    }


def _difference_map(
    reference: dict[str, Any],
    candidate: dict[str, Any],
    max_time_bins: int,
    max_frequency_bins: int,
) -> dict[str, Any]:
    if reference["samplerate"] != candidate["samplerate"]:
        return {
            "time_bins": [],
            "frequency_bins_hz": [],
            "energy_delta_db": [],
            "summary": {
                "comparison_available": False,
                "reason": "sample_rate_mismatch",
                "mean_abs_delta_db": None,
                "max_abs_delta_db": None,
                "changed_bin_count": 0,
                "changed_bin_ratio": 0.0,
                "delta_threshold_db": DEFAULT_DELTA_THRESHOLD_DB,
            },
        }

    shared_frames = min(reference["audio"].shape[0], candidate["audio"].shape[0])
    if shared_frames <= 0:
        return {
            "time_bins": [],
            "frequency_bins_hz": [],
            "energy_delta_db": [],
            "summary": {
                "comparison_available": False,
                "reason": "empty_audio",
                "mean_abs_delta_db": None,
                "max_abs_delta_db": None,
                "changed_bin_count": 0,
                "changed_bin_ratio": 0.0,
                "delta_threshold_db": DEFAULT_DELTA_THRESHOLD_DB,
            },
        }

    reference_audio = reference["audio"][:shared_frames]
    candidate_audio = candidate["audio"][:shared_frames]
    reference_spec = _spectrogram_matrix(
        reference_audio,
        reference["samplerate"],
        max_time_bins,
        max_frequency_bins,
    )
    candidate_spec = _spectrogram_matrix(
        candidate_audio,
        candidate["samplerate"],
        max_time_bins,
        max_frequency_bins,
    )
    shared_time_bins = min(reference_spec["energy_db"].shape[0], candidate_spec["energy_db"].shape[0])
    shared_frequency_bins = min(reference_spec["energy_db"].shape[1], candidate_spec["energy_db"].shape[1])
    if shared_time_bins <= 0 or shared_frequency_bins <= 0:
        return {
            "time_bins": [],
            "frequency_bins_hz": [],
            "energy_delta_db": [],
            "summary": {
                "comparison_available": False,
                "reason": "empty_spectrogram",
                "mean_abs_delta_db": None,
                "max_abs_delta_db": None,
                "changed_bin_count": 0,
                "changed_bin_ratio": 0.0,
                "delta_threshold_db": DEFAULT_DELTA_THRESHOLD_DB,
            },
        }

    delta = (
        candidate_spec["energy_db"][:shared_time_bins, :shared_frequency_bins]
        - reference_spec["energy_db"][:shared_time_bins, :shared_frequency_bins]
    )
    abs_delta = np.abs(delta)
    changed = abs_delta >= DEFAULT_DELTA_THRESHOLD_DB
    return {
        "time_bins": reference_spec["time_bins"][:shared_time_bins].tolist(),
        "frequency_bins_hz": reference_spec["frequency_bins_hz"][:shared_frequency_bins].tolist(),
        "energy_delta_db": delta.tolist(),
        "summary": {
            "comparison_available": True,
            "reason": None,
            "mean_abs_delta_db": float(np.mean(abs_delta)),
            "max_abs_delta_db": float(np.max(abs_delta)),
            "changed_bin_count": int(np.count_nonzero(changed)),
            "changed_bin_ratio": float(np.mean(changed)),
            "delta_threshold_db": DEFAULT_DELTA_THRESHOLD_DB,
        },
    }


def _metric_cards(analysis: dict[str, Any]) -> dict[str, Any]:
    return _metric_cards_from_summary(analysis)


def _metric_cards_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "duration_seconds": _safe_number(summary.get("duration_seconds")),
        "sample_rate": _safe_int(summary.get("samplerate")),
        "channel_count": _safe_int(summary.get("channels")),
        "peak_dbfs": _safe_number(summary.get("peak_dbfs")),
        "rms_dbfs": _safe_number(summary.get("rms_dbfs")),
        "loudness_lufs_approx": _safe_number(summary.get("loudness_lufs_approx")),
        "clipping_sample_count": _safe_int(summary.get("clipping_sample_count")),
        "spectral_centroid_hz": _safe_number(summary.get("spectral_centroid_hz")),
        "spectral_rolloff_95_hz": _safe_number(summary.get("spectral_rolloff_95_hz")),
        "dynamic_range_estimate_db": _safe_number(summary.get("dynamic_range_estimate_db")),
        "stereo_correlation": _safe_number(summary.get("stereo_correlation")),
        "side_energy_ratio": _safe_number(summary.get("side_energy_ratio")),
    }


def _single_file_tooltip_regions(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    regions: list[dict[str, Any]] = []
    if analysis.get("clipping_sample_count", 0) > 0:
        regions.append(
            {
                "label": "spectral energy changed",
                "metric": "clipping_sample_count",
                "value": int(analysis["clipping_sample_count"]),
                "status": "warning",
                "time_start_seconds": 0.0,
                "time_end_seconds": analysis.get("duration_seconds", 0.0),
            }
        )
    return regions


def _comparison_tooltip_regions(
    comparison: dict[str, Any],
    difference_map: dict[str, Any],
) -> list[dict[str, Any]]:
    regions: list[dict[str, Any]] = []
    metrics = comparison.get("comparison_metrics", {})
    reference = comparison.get("reference", {})
    candidate = comparison.get("candidate", {})

    clipping_delta = _safe_number(
        (candidate.get("clipping_sample_count") or 0) - (reference.get("clipping_sample_count") or 0)
    )
    if clipping_delta is not None and clipping_delta < 0:
        regions.append(_tooltip("clipping reduced", "clipping_sample_count_delta", clipping_delta, "improved"))

    for label, metric, threshold in (
        ("peak changed", "peak_delta", 0.001),
        ("RMS changed", "rms_delta", 0.001),
        ("dynamic range changed", "dynamic_range_delta_db", 0.1),
        ("spectral centroid changed", "spectral_centroid_delta_hz", 1.0),
        ("spectral rolloff changed", "spectral_rolloff_delta_hz", 1.0),
        ("stereo correlation changed", "stereo_correlation_delta", 0.001),
        ("side energy changed", "side_energy_ratio_delta", 0.001),
    ):
        value = _safe_number(metrics.get(metric))
        if value is not None and abs(value) > threshold:
            regions.append(_tooltip(label, metric, value, "changed"))

    summary = difference_map.get("summary", {})
    mean_abs_delta = _safe_number(summary.get("mean_abs_delta_db"))
    if mean_abs_delta is not None and mean_abs_delta >= DEFAULT_DELTA_THRESHOLD_DB:
        regions.append(_tooltip("spectral energy changed", "mean_abs_delta_db", mean_abs_delta, "changed"))

    return [region for region in regions if region["label"] in ALLOWED_TOOLTIP_LABELS][:16]


def _tooltip(label: str, metric: str, value: float, status: str) -> dict[str, Any]:
    return {
        "label": label,
        "metric": metric,
        "value": value,
        "status": status,
    }


def _next_power_of_two(value: int) -> int:
    value = max(1, int(value))
    return 1 << (value - 1).bit_length()


def _safe_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number


def _safe_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(number):
        return None
    return number


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return _json_safe_value(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if not np.isfinite(value):
            return None
        return value
    return value
