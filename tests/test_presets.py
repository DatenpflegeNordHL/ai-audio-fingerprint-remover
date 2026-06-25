from __future__ import annotations

import pytest

from audio_quality_humanizer.processing.presets import SUPPORTED_PRESETS, _validate_and_cap, get_preset


def test_all_supported_presets_load():
    for name in SUPPORTED_PRESETS:
        preset = get_preset(name)
        assert preset["name"] == name
        assert "safe_peak_dbfs" in preset
        assert "soft_saturation_drive" in preset
        assert "soft_saturation_mix" in preset


def test_unknown_preset_raises_clear_error():
    with pytest.raises(ValueError, match="Unknown humanize preset"):
        get_preset("unknown")


def test_saturation_drive_and_mix_are_capped_safely():
    preset = get_preset("balanced")
    preset["soft_saturation_drive"] = 2.0
    preset["soft_saturation_mix"] = 1.0

    capped = _validate_and_cap(preset)

    assert capped["soft_saturation_drive"] == 1.05
    assert capped["soft_saturation_mix"] == 0.25


def test_deharsh_and_demud_reductions_are_capped_safely():
    preset = get_preset("afro-club")
    preset["deharsh_db"] = -6.0
    preset["demud_db"] = -6.0

    capped = _validate_and_cap(preset)

    assert capped["deharsh_db"] == -1.5
    assert capped["demud_db"] == -1.0


def test_low_end_mono_only_enabled_for_club_presets():
    assert get_preset("subtle")["low_end_mono_hz"] == 0.0
    assert get_preset("balanced")["low_end_mono_hz"] == 0.0
    assert get_preset("vocal")["low_end_mono_hz"] == 0.0
    assert get_preset("club")["low_end_mono_hz"] == 120.0
    assert get_preset("afro-club")["low_end_mono_hz"] == 120.0
