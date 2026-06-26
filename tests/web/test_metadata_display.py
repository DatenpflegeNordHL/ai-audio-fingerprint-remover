from __future__ import annotations

import json

from audio_quality_humanizer.web.metadata_display import build_metadata_display, summarize_metadata_value


def test_metadata_display_summarizes_embedded_cover_dict():
    report = {
        "metadata": {
            "metadata_handler": "synthetic",
            "metadata_read_error": None,
            "detected_metadata_keys": ["APIC:Cover"],
            "metadata_values": {
                "APIC:Cover": {
                    "mime": "image/jpeg",
                    "type": 3,
                    "data": b"\x00" * 12,
                }
            },
        }
    }

    display = build_metadata_display(report)
    value = display["metadata_values"]["APIC:Cover"]

    assert value["embedded_cover"] is True
    assert value["mime"] == "image/jpeg"
    assert value["type"] == "cover_front"
    assert value["size_bytes"] == 12
    assert value["display_value"] == "[embedded image omitted]"
    assert display["detected_metadata_keys"] == ["APIC:Cover"]
    json.dumps(display, allow_nan=False)


def test_metadata_display_truncates_long_text_values():
    summary = summarize_metadata_value("comment", "x" * 1200)

    assert summary["truncated"] is True
    assert summary["length_chars"] == 1200
    assert len(summary["display_value"]) == 503
