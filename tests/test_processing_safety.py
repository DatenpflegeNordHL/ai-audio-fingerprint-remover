from __future__ import annotations

from audio_quality_humanizer.processing.safety_gates import evaluate_processing_safety


def _analysis(**overrides):
    report = {
        "samplerate": 48000,
        "channels": 2,
        "duration_seconds": 1.0,
        "peak_dbfs": -3.0,
        "rms_dbfs": -18.0,
        "loudness_lufs_approx": -18.0,
        "crest_factor_db": 12.0,
        "clipping_sample_count": 0,
        "near_clip_sample_count": 0,
        "dynamic_range_estimate_db": 10.0,
        "stereo_correlation": 0.8,
        "side_energy_ratio": 0.1,
        "low_end_stereo_warning": False,
        "harshness_energy_ratio_6000_12000_hz": 0.01,
        "low_mid_mud_energy_ratio_180_450_hz": 0.01,
        "shimmer_band_energy_ratio_5000_8000_hz": 0.01,
    }
    report.update(overrides)
    return report


def _comparison(**overrides):
    report = {
        "passed": True,
        "compatibility": {
            "samplerate_match": True,
            "channels_match": True,
            "duration_delta_ms": 0.0,
        },
        "metric_deltas": {
            "rms_dbfs_delta": 0.0,
            "loudness_lufs_approx_delta": 0.0,
            "crest_factor_db_delta": 0.0,
            "dynamic_range_estimate_db_delta": 0.0,
            "harshness_energy_ratio_delta": 0.0,
            "low_mid_mud_energy_ratio_delta": 0.0,
            "shimmer_band_energy_ratio_delta": 0.0,
            "side_energy_ratio_delta": 0.0,
            "near_clip_sample_count_delta": 0,
            "low_band_energy_ratio_delta": 0.0,
        },
    }
    report.update(overrides)
    return report


def test_safety_gate_fails_blocking_conditions():
    before = _analysis()
    after = _analysis(
        clipping_sample_count=1,
        rms_dbfs=-80.0,
        crest_factor_db=9.0,
        samplerate=44100,
        channels=1,
    )
    comparison = _comparison(
        passed=False,
        compatibility={
            "samplerate_match": False,
            "channels_match": False,
            "duration_delta_ms": 25.0,
        },
        metric_deltas={
            "rms_dbfs_delta": -62.0,
            "loudness_lufs_approx_delta": -62.0,
            "crest_factor_db_delta": -3.0,
            "dynamic_range_estimate_db_delta": -4.0,
            "harshness_energy_ratio_delta": 0.0,
            "low_mid_mud_energy_ratio_delta": 0.0,
            "shimmer_band_energy_ratio_delta": 0.0,
            "side_energy_ratio_delta": 0.0,
            "near_clip_sample_count_delta": 0,
            "low_band_energy_ratio_delta": 0.0,
        },
    )

    safety = evaluate_processing_safety(before, after, comparison, preset="balanced", target="streaming")

    assert safety["passed"] is False
    joined = " ".join(safety["blocking_issues"])
    assert "clipping" in joined
    assert "almost silent" in joined
    assert "RMS changed" in joined
    assert "Crest factor dropped" in joined
    assert "Sample rate changed" in joined
    assert "Channel count changed" in joined
