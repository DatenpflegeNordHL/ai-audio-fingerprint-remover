from __future__ import annotations

import json

from audio_quality_humanizer.validation.performance import (
    add_file_sizes,
    collect_file_stats,
    estimate_report_size,
    measure_operation,
)


def test_measure_operation_context_returns_elapsed_and_platform_metadata():
    with measure_operation("unit_test") as metrics:
        value = sum([1, 2, 3])

    assert value == 6
    assert metrics["operation"] == "unit_test"
    assert metrics["elapsed_seconds"] >= 0.0
    assert metrics["python_version"]
    assert metrics["platform"]
    json.dumps(metrics)


def test_measure_operation_callable_returns_result_and_metrics():
    measured = measure_operation("callable_test", lambda: "done")

    assert measured["result"] == "done"
    assert measured["performance"]["operation"] == "callable_test"
    assert measured["performance"]["elapsed_seconds"] >= 0.0


def test_collect_file_stats_and_report_size_are_json_safe(tmp_path):
    path = tmp_path / "report.json"
    path.write_text('{"ok": true}\n', encoding="utf-8")

    stats = collect_file_stats(path)
    report_size = estimate_report_size(path)

    assert stats["exists"] is True
    assert stats["is_file"] is True
    assert stats["size_bytes"] > 0
    assert report_size["report_size_bytes"] == stats["size_bytes"]
    json.dumps(stats)
    json.dumps(report_size)


def test_add_file_sizes_updates_optional_fields(tmp_path):
    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "output.wav"
    report_path = tmp_path / "report.json"
    input_path.write_bytes(b"input")
    output_path.write_bytes(b"output")
    report_path.write_text("{}\n", encoding="utf-8")
    metrics = {"operation": "test"}

    updated = add_file_sizes(metrics, input_path=input_path, output_path=output_path, report_path=report_path)

    assert updated["input_size_bytes"] == 5
    assert updated["output_size_bytes"] == 6
    assert updated["report_size_bytes"] == 3
