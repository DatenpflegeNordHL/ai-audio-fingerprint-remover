from __future__ import annotations

from pathlib import Path

import pytest

from audio_quality_humanizer.validation.manifest import load_manifest, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_example_manifest_shape_validates():
    manifest_path = ROOT / "examples" / "validation_manifest.example.json"

    manifest = validate_manifest(load_manifest(manifest_path), manifest_path)

    assert manifest["project"] == "Dirty D. Noir local validation set"
    assert manifest["target"] == "club"
    assert len(manifest["samples"]) == 2
    assert manifest["samples"][0]["id"] == "afro_club_01"
    assert manifest["samples"][0]["presets"] == ["subtle", "club", "afro-club"]


def test_relative_paths_resolve_relative_to_manifest(tmp_path):
    manifest_path = tmp_path / "manifests" / "validation.json"
    manifest_path.parent.mkdir()
    manifest = {
        "samples": [
            {
                "id": "track_01",
                "path": "../validation_samples/track_01.wav",
            }
        ]
    }

    validated = validate_manifest(manifest, manifest_path)

    expected = (manifest_path.parent / "../validation_samples/track_01.wav").resolve()
    assert validated["samples"][0]["resolved_path"] == str(expected)


def test_missing_samples_fails_validation(tmp_path):
    with pytest.raises(ValueError, match="samples"):
        validate_manifest({"project": "missing"}, tmp_path / "validation.json")


def test_invalid_preset_fails_validation(tmp_path):
    manifest = {
        "samples": [
            {
                "id": "track_01",
                "path": "track_01.wav",
                "presets": ["subtle", "not-a-preset"],
            }
        ]
    }

    with pytest.raises(ValueError, match="Unsupported preset"):
        validate_manifest(manifest, tmp_path / "validation.json")


def test_invalid_target_fails_validation(tmp_path):
    manifest = {
        "target": "not-a-target",
        "samples": [
            {
                "id": "track_01",
                "path": "track_01.wav",
            }
        ],
    }

    with pytest.raises(ValueError, match="Unsupported manifest target"):
        validate_manifest(manifest, tmp_path / "validation.json")
