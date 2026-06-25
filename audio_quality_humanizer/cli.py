"""Command-line interface for audio-quality-humanizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from audio_quality_humanizer.metadata.cleaner import (
    clean_metadata,
    inspect_metadata,
    inspect_provenance,
)
from audio_quality_humanizer.reports.json_report import write_json_report


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        report = args.handler(args)
        if args.report:
            write_json_report(report, Path(args.report))
        print(_status_message(report, args.report))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-humanizer",
        description="Inspect and clean ordinary audio metadata locally.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_metadata_parser = subparsers.add_parser(
        "inspect-metadata",
        help="Inspect audio metadata and classify keys.",
    )
    inspect_metadata_parser.add_argument("input", type=Path)
    inspect_metadata_parser.add_argument("--report", type=Path)
    inspect_metadata_parser.set_defaults(handler=_handle_inspect_metadata)

    inspect_provenance_parser = subparsers.add_parser(
        "inspect-provenance",
        help="Report metadata keys that may need provenance review.",
    )
    inspect_provenance_parser.add_argument("input", type=Path)
    inspect_provenance_parser.add_argument("--report", type=Path)
    inspect_provenance_parser.set_defaults(handler=_handle_inspect_provenance)

    clean_metadata_parser = subparsers.add_parser(
        "clean-metadata",
        help="Copy a file and remove ordinary metadata where supported.",
    )
    clean_metadata_parser.add_argument("input", type=Path)
    clean_metadata_parser.add_argument("output", type=Path)
    clean_metadata_parser.add_argument("--report", type=Path)
    clean_metadata_parser.set_defaults(handler=_handle_clean_metadata)

    return parser


def _handle_inspect_metadata(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    return inspect_metadata(args.input)


def _handle_inspect_provenance(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    return inspect_provenance(args.input)


def _handle_clean_metadata(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    return clean_metadata(args.input, args.output)


def _require_input(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")


def _status_message(report: dict, report_path: Path | None) -> str:
    action = report.get("action", "completed")
    suffix = f"; report written to {report_path}" if report_path else ""
    if action == "clean_metadata":
        removed_count = len(report.get("removed_ordinary_metadata_keys", []))
        warning_count = len(report.get("warnings", []))
        return f"cleaned metadata copy; removed {removed_count} ordinary keys; warnings {warning_count}{suffix}"
    if action == "inspect_provenance":
        key_count = len(report.get("possible_provenance_keys", []))
        return f"provenance inspection complete; possible keys {key_count}{suffix}"
    key_count = len(report.get("metadata", {}).get("detected_metadata_keys", []))
    return f"metadata inspection complete; detected keys {key_count}{suffix}"


if __name__ == "__main__":
    raise SystemExit(main())
