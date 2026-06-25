"""Load and validate local validation sample manifests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from audio_quality_humanizer.analysis.release_check import SUPPORTED_TARGETS
from audio_quality_humanizer.processing.presets import SUPPORTED_PRESETS


def load_manifest(path: Path) -> dict:
    """Load a JSON validation manifest."""

    path = Path(path)
    with path.open("r", encoding="utf-8") as file_obj:
        manifest = json.load(file_obj)
    if not isinstance(manifest, dict):
        raise ValueError("Validation manifest must be a JSON object.")
    return manifest


def validate_manifest(manifest: dict, manifest_path: Path) -> dict:
    """Validate manifest shape and resolve sample paths without loading audio."""

    if "samples" not in manifest:
        raise ValueError("Validation manifest must contain samples.")
    samples = manifest["samples"]
    if not isinstance(samples, list):
        raise ValueError("Validation manifest samples must be a list.")

    manifest_path = Path(manifest_path)
    manifest_dir = manifest_path.parent.resolve()
    manifest_target = manifest.get("target")
    if manifest_target is not None:
        manifest_target = _validate_target(manifest_target, "manifest target")

    normalized_samples = []
    seen_ids = set()
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            raise ValueError(f"Validation sample at index {index} must be an object.")
        normalized = _validate_sample(sample, index, manifest_dir)
        if normalized["id"] in seen_ids:
            raise ValueError(f"Validation sample id must be unique: {normalized['id']}")
        seen_ids.add(normalized["id"])
        normalized_samples.append(normalized)

    return {
        "project": manifest.get("project"),
        "target": manifest_target,
        "samples": normalized_samples,
    }


def _validate_sample(sample: dict[str, Any], index: int, manifest_dir: Path) -> dict:
    sample_id = _required_string(sample, "id", index)
    sample_path = _required_string(sample, "path", index)
    resolved_path = Path(sample_path).expanduser()
    if not resolved_path.is_absolute():
        resolved_path = manifest_dir / resolved_path
    resolved_path = resolved_path.resolve()

    normalized = {
        "id": sample_id,
        "path": sample_path,
        "resolved_path": str(resolved_path),
    }
    if "target" in sample and sample["target"] is not None:
        normalized["target"] = _validate_target(sample["target"], f"sample {sample_id} target")
    if "presets" in sample and sample["presets"] is not None:
        normalized["presets"] = _validate_presets(sample["presets"], sample_id)
    if "notes" in sample:
        normalized["notes"] = sample["notes"]
    return normalized


def _required_string(sample: dict[str, Any], key: str, index: int) -> str:
    value = sample.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Validation sample at index {index} must contain non-empty {key}.")
    return value


def _validate_target(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string.")
    normalized = value.casefold()
    if normalized not in SUPPORTED_TARGETS:
        supported = ", ".join(SUPPORTED_TARGETS)
        raise ValueError(f"Unsupported {label}: {value}. Supported targets: {supported}")
    return normalized


def _validate_presets(value: Any, sample_id: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"Sample {sample_id} presets must be a list.")
    presets = []
    for preset in value:
        if not isinstance(preset, str):
            raise ValueError(f"Sample {sample_id} preset names must be strings.")
        normalized = preset.casefold()
        if normalized not in SUPPORTED_PRESETS:
            supported = ", ".join(SUPPORTED_PRESETS)
            raise ValueError(f"Unsupported preset for sample {sample_id}: {preset}. Supported presets: {supported}")
        presets.append(normalized)
    return presets
