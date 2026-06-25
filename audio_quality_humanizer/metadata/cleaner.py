"""Conservative metadata inspection and cleaning."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from typing import Any

from mutagen import File as MutagenFile


POSSIBLE_PROVENANCE_PATTERNS = (
    "c2pa",
    "content_credentials",
    "contentcredentials",
    "manifest",
    "signature",
    "signed",
    "provenance",
    "origin",
    "generated_by",
    "generator",
    "ai_tool",
    "model",
    "prompt",
    "seed",
    "creator_tool",
    "software_agent",
)


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest for a file."""

    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_metadata(path: Path) -> dict:
    """Inspect file metadata and classify detected keys."""

    path = Path(path)
    file_info = _file_info(path)
    metadata_result = _read_metadata(path)
    classified = _classify_metadata_keys(metadata_result["detected_metadata_keys"])
    warnings = _warnings_for_possible_provenance(
        classified["possible_provenance_keys"],
        "Possible provenance-related metadata keys were detected and should be reviewed manually.",
    )

    return {
        "action": "inspect_metadata",
        "file_info": file_info,
        "warnings": warnings,
        "metadata": {
            **metadata_result,
            **classified,
            "warnings": warnings,
        },
    }


def inspect_provenance(path: Path) -> dict:
    """Inspect metadata keys that may indicate provenance or generation context."""

    metadata_report = inspect_metadata(path)
    possible_keys = metadata_report["metadata"]["possible_provenance_keys"]
    warnings = _warnings_for_possible_provenance(
        possible_keys,
        "Possible provenance-related metadata keys were detected and should be reviewed manually.",
    )

    return {
        "action": "inspect_provenance",
        "file_info": metadata_report["file_info"],
        "possible_provenance_keys": possible_keys,
        "ordinary_metadata_keys": metadata_report["metadata"]["ordinary_metadata_keys"],
        "detected_metadata_keys": metadata_report["metadata"]["detected_metadata_keys"],
        "warnings": warnings,
    }


def clean_metadata(input_path: Path, output_path: Path) -> dict:
    """Copy an audio file and remove ordinary metadata where mutagen supports it."""

    input_path = Path(input_path)
    output_path = Path(output_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    before = inspect_metadata(input_path)
    ordinary_keys = before["metadata"]["ordinary_metadata_keys"]
    possible_provenance_keys = before["metadata"]["possible_provenance_keys"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_path, output_path)

    removed_keys: list[str] = []
    removal_errors: list[dict[str, str]] = []
    metadata_handler_available = False

    try:
        audio = MutagenFile(output_path)
        tags = getattr(audio, "tags", None) if audio is not None else None
        metadata_handler_available = tags is not None
        if tags is not None:
            for key in ordinary_keys:
                try:
                    del tags[key]
                    removed_keys.append(key)
                except Exception as exc:  # mutagen tag containers vary by format.
                    removal_errors.append({"key": key, "error": str(exc)})
            if removed_keys:
                audio.save()
    except Exception as exc:
        removal_errors.append({"key": "*", "error": str(exc)})

    after = inspect_metadata(output_path)
    warnings = _warnings_for_possible_provenance(
        possible_provenance_keys,
        "Possible provenance-related metadata keys were reported and were not targeted for removal.",
    )

    return {
        "action": "clean_metadata",
        "action_taken": "copied_input_and_removed_ordinary_metadata_where_supported",
        "input_file_info": before["file_info"],
        "output_file_info": after["file_info"],
        "metadata_handler_available": metadata_handler_available,
        "ordinary_metadata_keys_before": ordinary_keys,
        "possible_provenance_keys_before": possible_provenance_keys,
        "removed_ordinary_metadata_keys": removed_keys,
        "remaining_metadata_keys": after["metadata"]["detected_metadata_keys"],
        "removal_errors": removal_errors,
        "warnings": warnings,
    }


def _file_info(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _read_metadata(path: Path) -> dict[str, Any]:
    try:
        audio = MutagenFile(path)
    except Exception as exc:
        return {
            "metadata_handler": None,
            "metadata_read_error": str(exc),
            "detected_metadata_keys": [],
            "metadata_values": {},
        }

    if audio is None:
        return {
            "metadata_handler": None,
            "metadata_read_error": None,
            "detected_metadata_keys": [],
            "metadata_values": {},
        }

    tags = getattr(audio, "tags", None)
    if tags is None:
        return {
            "metadata_handler": audio.__class__.__name__,
            "metadata_read_error": None,
            "detected_metadata_keys": [],
            "metadata_values": {},
        }

    keys = sorted(str(key) for key in tags.keys())
    return {
        "metadata_handler": audio.__class__.__name__,
        "metadata_read_error": None,
        "detected_metadata_keys": keys,
        "metadata_values": {key: _json_safe(tags[key]) for key in keys},
    }


def _classify_metadata_keys(keys: list[str]) -> dict[str, list[str]]:
    possible = []
    ordinary = []
    for key in keys:
        key_lower = key.casefold()
        if any(pattern in key_lower for pattern in POSSIBLE_PROVENANCE_PATTERNS):
            possible.append(key)
        else:
            ordinary.append(key)
    return {
        "ordinary_metadata_keys": ordinary,
        "possible_provenance_keys": possible,
    }


def _warnings_for_possible_provenance(keys: list[str], message: str) -> list[str]:
    return [message] if keys else []


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return str(value)
