"""Safe metadata display summaries for the private web dashboard."""

from __future__ import annotations

from typing import Any


MAX_DISPLAY_CHARS = 500
IMAGE_KEY_MARKERS = ("apic", "cover", "picture", "metadata_block_picture", "covr")


def build_metadata_display(metadata_report: dict[str, Any]) -> dict[str, Any]:
    """Build a dashboard-safe metadata summary without large embedded values."""

    metadata = metadata_report.get("metadata", {})
    keys = list(metadata.get("detected_metadata_keys", []))
    values = metadata.get("metadata_values", {})
    display_values: dict[str, dict[str, Any]] = {}
    embedded_images: list[dict[str, Any]] = []

    for key in keys:
        value = values.get(key)
        summary = summarize_metadata_value(key, value)
        display_values[key] = summary
        if summary.get("embedded_cover"):
            embedded_images.append(summary)

    return {
        "detected_metadata_keys": keys,
        "metadata_handler": metadata.get("metadata_handler"),
        "metadata_read_error": metadata.get("metadata_read_error"),
        "metadata_values": display_values,
        "embedded_images": embedded_images,
        "display_truncation_chars": MAX_DISPLAY_CHARS,
    }


def summarize_metadata_value(key: str, value: Any) -> dict[str, Any]:
    """Summarize one metadata value for dashboard display."""

    if _is_embedded_image_key(key) or _looks_like_embedded_image(value):
        return _embedded_image_summary(key, value)

    display_value = _stringify(value)
    truncated = len(display_value) > MAX_DISPLAY_CHARS
    if truncated:
        display_value = display_value[:MAX_DISPLAY_CHARS] + "..."

    return {
        "key": key,
        "display_value": display_value,
        "truncated": truncated,
        "length_chars": len(_stringify(value)),
    }


def _embedded_image_summary(key: str, value: Any) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "key": key,
        "embedded_cover": True,
        "display_value": "[embedded image omitted]",
    }
    if isinstance(value, dict):
        mime = value.get("mime") or value.get("mime_type") or value.get("format")
        cover_type = value.get("type") or value.get("picture_type")
        data = value.get("data")
        if mime is not None:
            summary["mime"] = _stringify(mime)
        if cover_type is not None:
            summary["type"] = _normalize_cover_type(cover_type)
        size = _data_size(data)
        if size is not None:
            summary["size_bytes"] = size
    elif isinstance(value, (bytes, bytearray)):
        summary["size_bytes"] = len(value)
    elif value is not None:
        summary["size_bytes"] = len(_stringify(value).encode("utf-8"))
    if "type" not in summary and "cover" in key.casefold():
        summary["type"] = "cover_front"
    return summary


def _is_embedded_image_key(key: str) -> bool:
    normalized = key.casefold()
    return any(marker in normalized for marker in IMAGE_KEY_MARKERS)


def _looks_like_embedded_image(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    mime = _stringify(value.get("mime") or value.get("mime_type") or "")
    return mime.startswith("image/")


def _normalize_cover_type(value: Any) -> str:
    text = _stringify(value).casefold()
    if text in {"3", "front", "cover_front", "front_cover"}:
        return "cover_front"
    return _stringify(value)


def _data_size(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    if isinstance(value, list):
        return sum(_data_size(item) or 0 for item in value)
    return len(_stringify(value).encode("utf-8"))


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.hex()
    return str(value)
