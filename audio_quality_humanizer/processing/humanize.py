"""Conservative audio-quality processing."""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

from audio_quality_humanizer.analysis.audio_loader import load_audio
from audio_quality_humanizer.analysis.compare import compare_audio
from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.processing.presets import get_preset
from audio_quality_humanizer.processing.safety_gates import evaluate_processing_safety


EPSILON = 1e-12


def humanize_audio(
    input_path: Path,
    output_path: Path,
    preset: str = "subtle",
    target: str = "streaming",
) -> dict:
    """Apply conservative audible-quality processing without touching the input file."""

    input_path = Path(input_path)
    output_path = Path(output_path)
    _validate_paths(input_path, output_path)

    loaded = load_audio(input_path)
    before_analysis = analyze_audio(input_path)
    preset_config = get_preset(preset)
    audio = loaded["audio"].copy()
    processing_steps: list[dict] = []

    audio = _dc_offset_correction(audio, preset_config, processing_steps)
    audio = _apply_gain(audio, preset_config["gain_db"], processing_steps)
    audio = _safe_peak_ceiling(audio, preset_config["safe_peak_dbfs"], processing_steps, "initial_safe_peak")
    audio = _soft_saturation(audio, before_analysis, preset_config, processing_steps)
    audio = _conditional_band_attenuation(
        audio,
        loaded["samplerate"],
        before_analysis,
        preset_config,
        processing_steps,
        kind="deharsh",
    )
    audio = _conditional_band_attenuation(
        audio,
        loaded["samplerate"],
        before_analysis,
        preset_config,
        processing_steps,
        kind="demud",
    )
    audio = _low_end_mono(audio, loaded["samplerate"], preset_config, processing_steps)
    audio = _silence_trimming_disabled(audio, preset_config, processing_steps)
    audio = _safe_peak_ceiling(audio, preset_config["safe_peak_dbfs"], processing_steps, "final_safe_peak")

    _write_audio(output_path, audio, loaded)

    after_analysis = analyze_audio(output_path)
    comparison = compare_audio(input_path, output_path, target=target)
    safety = evaluate_processing_safety(before_analysis, after_analysis, comparison, preset_config["name"], target)
    reverted = False
    if not safety["passed"]:
        shutil.copy2(input_path, output_path)
        reverted = True

    return {
        "action": "humanize",
        "preset": preset_config["name"],
        "target": target,
        "input": str(input_path),
        "output": str(output_path),
        "passed": safety["passed"],
        "reverted": reverted,
        "processing_steps": processing_steps,
        "before_analysis": before_analysis,
        "after_analysis": after_analysis,
        "comparison": comparison,
        "safety": safety,
        "notes": [
            "Humanize applies conservative audible-quality processing only.",
            "Humanize does not evaluate or alter watermarks, fingerprints, provenance markers, origin markers, detector signals, C2PA markers, or attribution systems.",
            "The original input file is never modified.",
        ],
    }


def smooth_band_gain(
    freqs: np.ndarray,
    low_hz: float,
    high_hz: float,
    gain_db: float,
    transition_hz: float = 300.0,
) -> np.ndarray:
    """Build a smooth frequency gain mask with cosine transitions."""

    target_gain = 10.0 ** (gain_db / 20.0)
    transition_hz = max(float(transition_hz), EPSILON)
    gain = np.ones_like(freqs, dtype=np.float64)

    inside = (freqs >= low_hz) & (freqs <= high_hz)
    gain[inside] = target_gain

    lower_start = max(0.0, low_hz - transition_hz)
    lower = (freqs >= lower_start) & (freqs < low_hz)
    if np.any(lower):
        t = (freqs[lower] - lower_start) / max(low_hz - lower_start, EPSILON)
        gain[lower] = 1.0 + (target_gain - 1.0) * _half_cosine(t)

    upper = (freqs > high_hz) & (freqs <= high_hz + transition_hz)
    if np.any(upper):
        t = (freqs[upper] - high_hz) / transition_hz
        gain[upper] = target_gain + (1.0 - target_gain) * _half_cosine(t)

    return gain


def _validate_paths(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Output path must differ from input path so the original is never modified.")
    output_path.parent.mkdir(parents=True, exist_ok=True)


def _dc_offset_correction(audio: np.ndarray, preset: dict, steps: list[dict]) -> np.ndarray:
    if not preset["dc_offset_correction"]:
        steps.append({"name": "dc_offset_correction", "applied": False, "reason": "disabled"})
        return audio

    offsets = np.mean(audio, axis=0)
    should_apply = bool(np.any(np.abs(offsets) > 1e-6))
    steps.append(
        {
            "name": "dc_offset_correction",
            "applied": should_apply,
            "dc_offset_per_channel": [float(value) for value in offsets],
        }
    )
    if should_apply:
        return audio - offsets
    return audio


def _apply_gain(audio: np.ndarray, gain_db: float, steps: list[dict]) -> np.ndarray:
    if abs(gain_db) <= EPSILON:
        steps.append({"name": "gain", "applied": False, "gain_db": float(gain_db)})
        return audio
    scalar = 10.0 ** (gain_db / 20.0)
    steps.append({"name": "gain", "applied": True, "gain_db": float(gain_db)})
    return audio * scalar


def _safe_peak_ceiling(audio: np.ndarray, safe_peak_dbfs: float, steps: list[dict], name: str) -> np.ndarray:
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    target_linear = 10.0 ** (safe_peak_dbfs / 20.0)
    if peak > target_linear:
        scalar = target_linear / max(peak, EPSILON)
        steps.append(
            {
                "name": name,
                "applied": True,
                "safe_peak_dbfs": float(safe_peak_dbfs),
                "attenuation_db": float(20.0 * np.log10(scalar)),
            }
        )
        return audio * scalar
    steps.append(
        {
            "name": name,
            "applied": False,
            "safe_peak_dbfs": float(safe_peak_dbfs),
            "peak_linear": peak,
        }
    )
    return audio


def _soft_saturation(audio: np.ndarray, before_analysis: dict, preset: dict, steps: list[dict]) -> np.ndarray:
    drive = preset["soft_saturation_drive"]
    mix = preset["soft_saturation_mix"]
    if drive <= 1.0 or mix <= 0.0:
        steps.append({"name": "soft_saturation", "applied": False, "reason": "disabled"})
        return audio
    if before_analysis["clipping_sample_count"] > 0:
        steps.append({"name": "soft_saturation", "applied": False, "reason": "input_clipping_detected"})
        return audio
    if before_analysis["crest_factor_db"] < 8.0:
        steps.append({"name": "soft_saturation", "applied": False, "reason": "crest_factor_too_low"})
        return audio
    if before_analysis["peak_dbfs"] > -0.5:
        steps.append({"name": "soft_saturation", "applied": False, "reason": "peak_too_close_to_zero_dbfs"})
        return audio

    saturated = np.tanh(audio * drive) / np.tanh(drive)
    processed = (1.0 - mix) * audio + mix * saturated
    steps.append(
        {
            "name": "soft_saturation",
            "applied": True,
            "drive": float(drive),
            "mix": float(mix),
        }
    )
    return _limit_to_peak(processed, preset["safe_peak_dbfs"])


def _conditional_band_attenuation(
    audio: np.ndarray,
    samplerate: int,
    before_analysis: dict,
    preset: dict,
    steps: list[dict],
    *,
    kind: str,
) -> np.ndarray:
    enabled_key = f"{kind}_enabled"
    if not preset[enabled_key]:
        steps.append({"name": kind, "applied": False, "reason": "disabled"})
        return audio

    if before_analysis["duration_seconds"] < 0.25:
        steps.append({"name": kind, "applied": False, "reason": "file_too_short"})
        return audio

    if kind == "deharsh":
        metric_key = "harshness_energy_ratio_6000_12000_hz"
        should_apply = _has_warning(before_analysis, "harshness") or before_analysis[metric_key] > 0.18
        low_hz = preset["deharsh_low_hz"]
        high_hz = preset["deharsh_high_hz"]
        gain_db = preset["deharsh_db"]
    else:
        metric_key = "low_mid_mud_energy_ratio_180_450_hz"
        should_apply = _has_warning(before_analysis, "mud") or before_analysis[metric_key] > 0.35
        low_hz = preset["demud_low_hz"]
        high_hz = preset["demud_high_hz"]
        gain_db = preset["demud_db"]

    if not should_apply:
        steps.append({"name": kind, "applied": False, "reason": "metric_not_high"})
        return audio
    if samplerate / 2.0 <= low_hz:
        steps.append({"name": kind, "applied": False, "reason": "sample_rate_too_low_for_band"})
        return audio

    processed = _fft_band_attenuation(audio, samplerate, low_hz, high_hz, gain_db)
    steps.append(
        {
            "name": kind,
            "applied": True,
            "low_hz": float(low_hz),
            "high_hz": float(high_hz),
            "gain_db": float(gain_db),
            "trigger_metric": metric_key,
            "trigger_value": float(before_analysis[metric_key]),
        }
    )
    return _limit_to_peak(processed, preset["safe_peak_dbfs"])


def _fft_band_attenuation(
    audio: np.ndarray,
    samplerate: int,
    low_hz: float,
    high_hz: float,
    gain_db: float,
) -> np.ndarray:
    high_hz = min(high_hz, samplerate / 2.0)
    spectrum = np.fft.rfft(audio, axis=0)
    freqs = np.fft.rfftfreq(audio.shape[0], d=1.0 / samplerate)
    gain = smooth_band_gain(freqs, low_hz, high_hz, gain_db)[:, np.newaxis]
    processed = np.fft.irfft(spectrum * gain, n=audio.shape[0], axis=0)
    return np.asarray(processed, dtype=np.float64)


def _low_end_mono(audio: np.ndarray, samplerate: int, preset: dict, steps: list[dict]) -> np.ndarray:
    cutoff = preset["low_end_mono_hz"]
    if cutoff <= 0.0:
        steps.append({"name": "low_end_mono", "applied": False, "reason": "disabled"})
        return audio
    if audio.shape[1] < 2:
        steps.append({"name": "low_end_mono", "applied": False, "reason": "mono_input"})
        return audio
    if samplerate / 2.0 <= cutoff:
        steps.append({"name": "low_end_mono", "applied": False, "reason": "sample_rate_too_low"})
        return audio

    left = audio[:, 0]
    right = audio[:, 1]
    mid = (left + right) * 0.5
    side = (left - right) * 0.5
    side_spectrum = np.fft.rfft(side)
    freqs = np.fft.rfftfreq(side.shape[0], d=1.0 / samplerate)
    side_gain = _low_end_side_gain(freqs, cutoff)
    filtered_side = np.fft.irfft(side_spectrum * side_gain, n=side.shape[0])
    processed = audio.copy()
    processed[:, 0] = mid + filtered_side
    processed[:, 1] = mid - filtered_side
    steps.append(
        {
            "name": "low_end_mono",
            "applied": True,
            "cutoff_hz": float(cutoff),
            "transition_low_hz": 80.0,
            "transition_high_hz": 140.0,
        }
    )
    return _limit_to_peak(processed, preset["safe_peak_dbfs"])


def _low_end_side_gain(freqs: np.ndarray, cutoff: float) -> np.ndarray:
    low = max(0.0, cutoff - 40.0)
    high = cutoff + 20.0
    gain = np.ones_like(freqs, dtype=np.float64)
    gain[freqs <= low] = 0.0
    transition = (freqs > low) & (freqs < high)
    if np.any(transition):
        t = (freqs[transition] - low) / max(high - low, EPSILON)
        gain[transition] = _half_cosine(t)
    return gain


def _silence_trimming_disabled(audio: np.ndarray, preset: dict, steps: list[dict]) -> np.ndarray:
    steps.append(
        {
            "name": "silence_trimming",
            "applied": False,
            "trim_leading_silence_ms": float(preset["trim_leading_silence_ms"]),
            "trim_trailing_silence_ms": float(preset["trim_trailing_silence_ms"]),
            "reason": "disabled_for_current_presets",
        }
    )
    return audio


def _write_audio(output_path: Path, audio: np.ndarray, loaded: dict) -> None:
    if audio.shape[1] == 1:
        write_audio = audio[:, 0]
    else:
        write_audio = audio
    sf.write(output_path, write_audio, loaded["samplerate"], subtype=loaded["subtype"])


def _limit_to_peak(audio: np.ndarray, safe_peak_dbfs: float) -> np.ndarray:
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    target_linear = 10.0 ** (safe_peak_dbfs / 20.0)
    if peak > target_linear:
        return audio * (target_linear / max(peak, EPSILON))
    return audio


def _has_warning(analysis: dict, term: str) -> bool:
    return any(term in warning.casefold() for warning in analysis.get("warnings", []))


def _half_cosine(t: np.ndarray) -> np.ndarray:
    return 0.5 - 0.5 * np.cos(np.pi * np.clip(t, 0.0, 1.0))
