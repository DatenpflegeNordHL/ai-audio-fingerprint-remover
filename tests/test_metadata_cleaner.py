from __future__ import annotations

import soundfile as sf
from mutagen.id3 import TIT2, TXXX
from mutagen.wave import WAVE

from audio_quality_humanizer.metadata.cleaner import (
    clean_metadata,
    inspect_metadata,
    inspect_provenance,
)


def test_inspect_metadata_returns_file_info_and_sha256(tmp_path):
    input_path = tmp_path / "input.wav"
    sf.write(input_path, [0.0] * 800, 8000)

    report = inspect_metadata(input_path)

    assert report["file_info"]["path"] == str(input_path)
    assert report["file_info"]["extension"] == ".wav"
    assert report["file_info"]["size_bytes"] > 0
    assert len(report["file_info"]["sha256"]) == 64
    assert "detected_metadata_keys" in report["metadata"]


def test_clean_metadata_writes_output_and_reports_action(tmp_path):
    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "output.wav"
    sf.write(input_path, [0.0] * 800, 8000)

    report = clean_metadata(input_path, output_path)

    assert output_path.exists()
    assert report["action"] == "clean_metadata"
    assert report["action_taken"]
    assert report["output_file_info"]["sha256"]


def test_provenance_like_keys_are_classified(tmp_path):
    input_path = tmp_path / "tagged.wav"
    sf.write(input_path, [0.0] * 800, 8000)

    audio = WAVE(input_path)
    audio.add_tags()
    audio.tags.add(TIT2(encoding=3, text="Example title"))
    audio.tags.add(TXXX(encoding=3, desc="generator", text="Example tool"))
    audio.save()

    metadata_report = inspect_metadata(input_path)
    provenance_report = inspect_provenance(input_path)

    assert "TIT2" in metadata_report["metadata"]["ordinary_metadata_keys"]
    assert any(
        "generator" in key.casefold()
        for key in metadata_report["metadata"]["possible_provenance_keys"]
    )
    assert provenance_report["possible_provenance_keys"]
