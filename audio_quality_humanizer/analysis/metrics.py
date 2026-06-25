"""Read-only audio quality metrics."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from audio_quality_humanizer.analysis.audio_loader import load_audio
from audio_quality_humanizer.processing.guardrails import calculate_signal_guardrail_report


EPSILON = 1e-12


def analyze_audio(path: Path) -> dict:
    """Analyze audible quality and technical release-readiness metrics."""

    path = Path(path)
    loaded = load_audio(path)
    audio = loaded["audio"]
    samplerate = loaded["samplerate"]

    absolute = np.abs(audio)
    peak_linear = float(np.max(absolute)) if audio.size else 0.0
    peak_dbfs = _linear_to_db(peak_linear)
    rms_linear = float(np.sqrt(np.mean(np.square(audio)))) if audio.size else 0.0
    rms_dbfs = _linear_to_db(rms_linear)
    crest_factor_db = float(peak_dbfs - rms_dbfs) if rms_linear > 0 else 0.0
    dc_offset = [float(value) for value in np.mean(audio, axis=0)] if audio.size else []

    clipping_sample_count = int(np.count_nonzero(absolute >= 0.999))
    clipping_ratio = float(clipping_sample_count / audio.size) if audio.size else 0.0
    near_clip_sample_count = int(np.count_nonzero(absolute >= 0.98))

    frame_amplitude = np.max(absolute, axis=1) if audio.size else np.array([], dtype=np.float64)
    silence_metrics = _silence_metrics(frame_amplitude, samplerate)
    short_window_metrics = _short_window_metrics(audio, samplerate)
    spectrum_metrics = _spectrum_metrics(audio, samplerate)
    stereo_metrics = _stereo_metrics(audio, samplerate)
    guardrail_report = calculate_signal_guardrail_report(audio, samplerate=samplerate)["guardrails"]

    overcompression_warning = (
        short_window_metrics["dynamic_range_estimate_db"] < 6.0
        and rms_dbfs > -18.0
        and loaded["duration_seconds"] > 0.25
    ) or (crest_factor_db < 6.0 and rms_dbfs > -18.0)

    low_end_stereo_warning = bool(stereo_metrics["low_end_stereo_warning"])
    mono_compatibility_warning = bool(stereo_metrics["mono_compatibility_warning"])

    warnings = _quality_warnings(
        peak_dbfs=peak_dbfs,
        rms_dbfs=rms_dbfs,
        dc_offset=dc_offset,
        clipping_sample_count=clipping_sample_count,
        leading_silence_ms=silence_metrics["leading_silence_ms"],
        trailing_silence_ms=silence_metrics["trailing_silence_ms"],
        overcompression_warning=overcompression_warning,
        harshness_ratio=spectrum_metrics["harshness_energy_ratio_6000_12000_hz"],
        mud_ratio=spectrum_metrics["low_mid_mud_energy_ratio_180_450_hz"],
        stereo_correlation=stereo_metrics["stereo_correlation"],
        mono_compatibility_warning=mono_compatibility_warning,
        low_end_stereo_warning=low_end_stereo_warning,
    )

    return {
        "action": "analyze",
        "file_info": {
            "path": str(path),
            "extension": path.suffix.lower(),
            "size_bytes": path.stat().st_size,
        },
        "samplerate": loaded["samplerate"],
        "channels": loaded["channels"],
        "frames": loaded["frames"],
        "duration_seconds": loaded["duration_seconds"],
        "format": loaded["format"],
        "subtype": loaded["subtype"],
        "peak_linear": peak_linear,
        "peak_dbfs": peak_dbfs,
        "rms_linear": rms_linear,
        "rms_dbfs": rms_dbfs,
        "loudness_lufs_approx": rms_dbfs,
        "crest_factor_db": crest_factor_db,
        "dc_offset_per_channel": dc_offset,
        "clipping_sample_count": clipping_sample_count,
        "clipping_ratio": clipping_ratio,
        "near_clip_sample_count": near_clip_sample_count,
        **silence_metrics,
        **short_window_metrics,
        "overcompression_warning": overcompression_warning,
        **spectrum_metrics,
        "stereo_correlation": stereo_metrics["stereo_correlation"],
        "side_energy_ratio": stereo_metrics["side_energy_ratio"],
        "mono_compatibility_warning": mono_compatibility_warning,
        "low_end_stereo_warning": low_end_stereo_warning,
        "warnings": warnings,
        "guardrails": guardrail_report,
        "notes": [
            "loudness_lufs_approx is an RMS-based approximation and is not EBU/ITU compliant LUFS.",
            "Analysis is read-only and does not alter audio files.",
        ],
    }


def _linear_to_db(value: float) -> float:
    return float(20.0 * np.log10(max(float(value), EPSILON)))


def _silence_metrics(frame_amplitude: np.ndarray, samplerate: int) -> dict[str, float]:
    if frame_amplitude.size == 0 or samplerate <= 0:
        return {
            "leading_silence_ms": 0.0,
            "trailing_silence_ms": 0.0,
            "silence_ratio": 0.0,
            "very_quiet_ratio": 0.0,
        }

    silence_threshold = 10 ** (-60.0 / 20.0)
    very_quiet_threshold = 10 ** (-50.0 / 20.0)
    silent = frame_amplitude < silence_threshold
    leading_frames = _count_leading_true(silent)
    trailing_frames = _count_leading_true(silent[::-1])

    return {
        "leading_silence_ms": float(leading_frames / samplerate * 1000.0),
        "trailing_silence_ms": float(trailing_frames / samplerate * 1000.0),
        "silence_ratio": float(np.mean(silent)),
        "very_quiet_ratio": float(np.mean(frame_amplitude < very_quiet_threshold)),
    }


def _short_window_metrics(audio: np.ndarray, samplerate: int) -> dict[str, float]:
    if audio.size == 0 or samplerate <= 0:
        return {
            "short_window_rms_db_min": -240.0,
            "short_window_rms_db_max": -240.0,
            "short_window_rms_db_mean": -240.0,
            "dynamic_range_estimate_db": 0.0,
        }

    window = max(1, int(round(samplerate * 0.05)))
    mono = np.mean(audio, axis=1)
    values = []
    for start in range(0, len(mono), window):
        segment = mono[start : start + window]
        if segment.size:
            values.append(_linear_to_db(float(np.sqrt(np.mean(np.square(segment))))))

    rms_db = np.asarray(values, dtype=np.float64)
    active = rms_db[rms_db > -80.0]
    range_source = active if active.size else rms_db
    dynamic_range = float(np.percentile(range_source, 95) - np.percentile(range_source, 10))

    return {
        "short_window_rms_db_min": float(np.min(rms_db)),
        "short_window_rms_db_max": float(np.max(rms_db)),
        "short_window_rms_db_mean": float(np.mean(rms_db)),
        "dynamic_range_estimate_db": dynamic_range,
    }


def _spectrum_metrics(audio: np.ndarray, samplerate: int) -> dict[str, float]:
    if audio.size == 0 or samplerate <= 0:
        return _empty_spectrum_metrics()

    mono = np.mean(audio, axis=1)
    if mono.size < 2:
        return _empty_spectrum_metrics()

    mono = mono - np.mean(mono)
    windowed = mono * np.hanning(mono.size)
    spectrum = np.fft.rfft(windowed)
    magnitude = np.abs(spectrum)
    power = np.square(magnitude)
    freqs = np.fft.rfftfreq(mono.size, d=1.0 / samplerate)
    total_magnitude = float(np.sum(magnitude))
    total_power = float(np.sum(power))

    if total_power <= EPSILON or total_magnitude <= EPSILON:
        return _empty_spectrum_metrics()

    cumulative_power = np.cumsum(power)
    centroid = float(np.sum(freqs * magnitude) / (total_magnitude + EPSILON))
    rolloff_85 = _rolloff_frequency(freqs, cumulative_power, total_power, 0.85)
    rolloff_95 = _rolloff_frequency(freqs, cumulative_power, total_power, 0.95)
    flatness = float(np.exp(np.mean(np.log(power + EPSILON))) / (np.mean(power + EPSILON)))

    return {
        "spectral_centroid_hz": centroid,
        "spectral_rolloff_85_hz": rolloff_85,
        "spectral_rolloff_95_hz": rolloff_95,
        "spectral_flatness": flatness,
        "low_band_energy_ratio_20_120_hz": _band_energy_ratio(freqs, power, 20.0, 120.0),
        "low_mid_mud_energy_ratio_180_450_hz": _band_energy_ratio(freqs, power, 180.0, 450.0),
        "harshness_energy_ratio_6000_12000_hz": _band_energy_ratio(freqs, power, 6000.0, 12000.0),
        "shimmer_band_energy_ratio_5000_8000_hz": _band_energy_ratio(freqs, power, 5000.0, 8000.0),
    }


def _stereo_metrics(audio: np.ndarray, samplerate: int) -> dict[str, Any]:
    if audio.shape[1] < 2:
        return {
            "stereo_correlation": None,
            "side_energy_ratio": 0.0,
            "mono_compatibility_warning": False,
            "low_end_stereo_warning": False,
        }

    left = audio[:, 0]
    right = audio[:, 1]
    left_std = float(np.std(left))
    right_std = float(np.std(right))
    correlation = 1.0
    if left_std > EPSILON and right_std > EPSILON:
        correlation = float(np.corrcoef(left, right)[0, 1])

    mid = (left + right) * 0.5
    side = (left - right) * 0.5
    mid_energy = float(np.mean(np.square(mid)))
    side_energy = float(np.mean(np.square(side)))
    side_ratio = float(side_energy / (mid_energy + EPSILON))
    low_side_ratio = _low_band_side_ratio(mid, side, samplerate)

    return {
        "stereo_correlation": correlation,
        "side_energy_ratio": side_ratio,
        "mono_compatibility_warning": bool(correlation < 0.0 or side_ratio > 1.0),
        "low_end_stereo_warning": bool(low_side_ratio > 0.25),
    }


def _empty_spectrum_metrics() -> dict[str, float]:
    return {
        "spectral_centroid_hz": 0.0,
        "spectral_rolloff_85_hz": 0.0,
        "spectral_rolloff_95_hz": 0.0,
        "spectral_flatness": 0.0,
        "low_band_energy_ratio_20_120_hz": 0.0,
        "low_mid_mud_energy_ratio_180_450_hz": 0.0,
        "harshness_energy_ratio_6000_12000_hz": 0.0,
        "shimmer_band_energy_ratio_5000_8000_hz": 0.0,
    }


def _rolloff_frequency(
    freqs: np.ndarray,
    cumulative_power: np.ndarray,
    total_power: float,
    fraction: float,
) -> float:
    index = int(np.searchsorted(cumulative_power, total_power * fraction, side="left"))
    index = min(index, len(freqs) - 1)
    return float(freqs[index])


def _band_energy_ratio(freqs: np.ndarray, power: np.ndarray, low: float, high: float) -> float:
    mask = (freqs >= low) & (freqs <= high)
    total = float(np.sum(power))
    if total <= EPSILON or not np.any(mask):
        return 0.0
    return float(np.sum(power[mask]) / (total + EPSILON))


def _low_band_side_ratio(mid: np.ndarray, side: np.ndarray, samplerate: int) -> float:
    if samplerate <= 0 or mid.size < 2:
        return 0.0

    freqs = np.fft.rfftfreq(mid.size, d=1.0 / samplerate)
    low_mask = (freqs >= 20.0) & (freqs <= 120.0)
    if not np.any(low_mask):
        return 0.0

    window = np.hanning(mid.size)
    mid_power = np.square(np.abs(np.fft.rfft((mid - np.mean(mid)) * window)))
    side_power = np.square(np.abs(np.fft.rfft((side - np.mean(side)) * window)))
    return float(np.sum(side_power[low_mask]) / (np.sum(mid_power[low_mask]) + EPSILON))


def _count_leading_true(values: np.ndarray) -> int:
    count = 0
    for value in values:
        if not bool(value):
            break
        count += 1
    return count


def _quality_warnings(
    *,
    peak_dbfs: float,
    rms_dbfs: float,
    dc_offset: list[float],
    clipping_sample_count: int,
    leading_silence_ms: float,
    trailing_silence_ms: float,
    overcompression_warning: bool,
    harshness_ratio: float,
    mud_ratio: float,
    stereo_correlation: float | None,
    mono_compatibility_warning: bool,
    low_end_stereo_warning: bool,
) -> list[str]:
    warnings = []
    if clipping_sample_count > 0:
        warnings.append("Clipping detected in the audio samples.")
    if peak_dbfs > -1.0:
        warnings.append("Peak level is above -1.0 dBFS.")
    if rms_dbfs < -50.0:
        warnings.append("RMS level is very low; the file may be almost silent.")
    if any(abs(value) > 0.01 for value in dc_offset):
        warnings.append("Strong DC offset detected.")
    if overcompression_warning:
        warnings.append("Possible overcompression based on short-window dynamics and crest factor.")
    if harshness_ratio > 0.18:
        warnings.append("High harshness-band energy ratio detected as an audible quality issue.")
    if mud_ratio > 0.35:
        warnings.append("High low-mid mud energy ratio detected as an audible quality issue.")
    if stereo_correlation is not None and stereo_correlation < 0.1:
        warnings.append("Stereo correlation is very low or negative.")
    if mono_compatibility_warning:
        warnings.append("Potential mono compatibility issue based on stereo side energy.")
    if low_end_stereo_warning:
        warnings.append("Low-end stereo risk detected below about 120 Hz.")
    if leading_silence_ms > 3000.0 or trailing_silence_ms > 5000.0:
        warnings.append("Excessive leading or trailing silence detected.")
    return warnings
