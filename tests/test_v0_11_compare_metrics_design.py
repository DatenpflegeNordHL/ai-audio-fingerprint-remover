from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_MARKDOWN = ROOT / "docs" / "design" / "V0_11_0_COMPARE_METRICS.md"
DESIGN_JSON = ROOT / "docs" / "design" / "v0_11_0_compare_metrics.json"
REQUIRED_METRICS = {
    "rmse",
    "mean_absolute_error",
    "correlation",
    "snr_db_approx",
    "peak_before",
    "peak_after",
    "peak_delta",
    "rms_before",
    "rms_after",
    "rms_delta",
    "dynamic_range_before_db",
    "dynamic_range_after_db",
    "dynamic_range_delta_db",
    "spectral_centroid_before_hz",
    "spectral_centroid_after_hz",
    "spectral_centroid_delta_hz",
    "spectral_rolloff_before_hz",
    "spectral_rolloff_after_hz",
    "spectral_rolloff_delta_hz",
}
FORBIDDEN_METRIC_NAMES = {
    "watermark_score",
    "fingerprint_score",
    "detector_score",
    "evasion_score",
    "bypass_score",
    "recognition_score",
    "provenance_score",
    "detectability_score",
    "origin_score",
    "source_attribution_score",
}


def _design() -> dict:
    return json.loads(DESIGN_JSON.read_text(encoding="utf-8"))


def test_v0_11_compare_metrics_design_files_exist():
    assert DESIGN_MARKDOWN.exists()
    assert DESIGN_JSON.exists()


def test_v0_11_compare_metrics_design_records_gate_and_metrics():
    design = _design()

    assert design["version_target"] == "0.11.0"
    assert design["status"] == "implemented_safe_read_only_compare_metrics"
    assert design["deep_search_decision"] == "not_needed_internal_repo_only"
    assert design["deep_search_stop_rule_active"] is True
    assert REQUIRED_METRICS <= set(design["implemented_metrics"])
    assert FORBIDDEN_METRIC_NAMES <= set(design["rejected_metric_names"])


def test_v0_11_compare_metrics_design_preserves_safety_boundary():
    boundary = _design()["safety_boundary"]

    assert boundary["read_only_compare"] is True
    assert boundary["new_cli_command"] is False
    assert boundary["audio_modification"] is False
    assert boundary["release_check_scoring_change"] is False
    assert boundary["humanize_processing_change"] is False
    assert boundary["project_reborn_source_copied"] is False
    assert boundary["project_reborn_source_imported"] is False
    assert boundary["project_reborn_source_executed"] is False
    assert boundary["project_reborn_source_packaged"] is False
    assert boundary["project_reborn_source_exposed"] is False


def test_v0_11_compare_metrics_design_requires_real_validation_and_no_op():
    design = _design()

    assert design["real_local_validation_plan"]["required"] is True
    assert design["real_local_validation_plan"]["commit_outputs"] is False
    assert design["no_op_check_plan"]["required"] is True
