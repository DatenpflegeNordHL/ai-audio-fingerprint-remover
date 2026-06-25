"""Conservative humanize presets."""

from __future__ import annotations

from copy import deepcopy


SUPPORTED_PRESETS = ("subtle", "balanced", "club", "vocal", "afro-club")


_PRESET_DEFAULTS = {
    "name": "",
    "dc_offset_correction": True,
    "safe_peak_dbfs": -1.0,
    "gain_db": 0.0,
    "soft_saturation_drive": 1.0,
    "soft_saturation_mix": 0.0,
    "deharsh_enabled": False,
    "deharsh_db": 0.0,
    "deharsh_low_hz": 6000.0,
    "deharsh_high_hz": 12000.0,
    "demud_enabled": False,
    "demud_db": 0.0,
    "demud_low_hz": 180.0,
    "demud_high_hz": 450.0,
    "low_end_mono_hz": 0.0,
    "trim_leading_silence_ms": 0.0,
    "trim_trailing_silence_ms": 0.0,
}


_PRESETS = {
    "subtle": {
        "name": "subtle",
        "dc_offset_correction": True,
        "safe_peak_dbfs": -1.0,
    },
    "balanced": {
        "name": "balanced",
        "dc_offset_correction": True,
        "safe_peak_dbfs": -1.0,
        "soft_saturation_drive": 1.02,
        "soft_saturation_mix": 0.20,
        "deharsh_enabled": True,
        "deharsh_db": -0.7,
        "deharsh_low_hz": 6000.0,
        "deharsh_high_hz": 12000.0,
        "demud_enabled": True,
        "demud_db": -0.5,
        "demud_low_hz": 180.0,
        "demud_high_hz": 450.0,
    },
    "club": {
        "name": "club",
        "dc_offset_correction": True,
        "safe_peak_dbfs": -0.8,
        "soft_saturation_drive": 1.03,
        "soft_saturation_mix": 0.20,
        "low_end_mono_hz": 120.0,
    },
    "vocal": {
        "name": "vocal",
        "dc_offset_correction": True,
        "safe_peak_dbfs": -1.0,
        "soft_saturation_drive": 1.04,
        "soft_saturation_mix": 0.20,
        "deharsh_enabled": True,
        "deharsh_db": -1.0,
        "deharsh_low_hz": 7000.0,
        "deharsh_high_hz": 10000.0,
    },
    "afro-club": {
        "name": "afro-club",
        "dc_offset_correction": True,
        "safe_peak_dbfs": -0.8,
        "soft_saturation_drive": 1.03,
        "soft_saturation_mix": 0.20,
        "deharsh_enabled": True,
        "deharsh_db": -1.0,
        "deharsh_low_hz": 6000.0,
        "deharsh_high_hz": 12000.0,
        "demud_enabled": True,
        "demud_db": -0.5,
        "demud_low_hz": 180.0,
        "demud_high_hz": 450.0,
        "low_end_mono_hz": 120.0,
    },
}


def get_preset(name: str) -> dict:
    """Return a validated conservative preset by name."""

    normalized = name.casefold()
    if normalized not in _PRESETS:
        supported = ", ".join(SUPPORTED_PRESETS)
        raise ValueError(f"Unknown humanize preset: {name}. Supported presets: {supported}")

    preset = deepcopy(_PRESET_DEFAULTS)
    preset.update(_PRESETS[normalized])
    return _validate_and_cap(preset)


def _validate_and_cap(preset: dict) -> dict:
    preset["soft_saturation_drive"] = _clamp(float(preset["soft_saturation_drive"]), 1.0, 1.05)
    preset["soft_saturation_mix"] = _clamp(float(preset["soft_saturation_mix"]), 0.0, 0.25)
    preset["deharsh_db"] = max(float(preset["deharsh_db"]), -1.5)
    preset["demud_db"] = max(float(preset["demud_db"]), -1.0)
    preset["low_end_mono_hz"] = float(preset["low_end_mono_hz"])
    if preset["low_end_mono_hz"] != 0.0 and not 80.0 <= preset["low_end_mono_hz"] <= 140.0:
        raise ValueError("low_end_mono_hz must be 0 or between 80 and 140 Hz.")
    return preset


def _clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)
