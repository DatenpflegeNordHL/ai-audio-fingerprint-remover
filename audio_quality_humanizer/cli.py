"""Command-line interface for audio-quality-humanizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from audio_quality_humanizer.analysis.compare import compare_audio
from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.analysis.release_check import SUPPORTED_TARGETS, release_check
from audio_quality_humanizer.metadata.cleaner import (
    clean_metadata,
    inspect_metadata,
    inspect_provenance,
)
from audio_quality_humanizer.processing.humanize import humanize_audio
from audio_quality_humanizer.processing.presets import SUPPORTED_PRESETS
from audio_quality_humanizer.reports.json_report import write_json_report
from audio_quality_humanizer.reports.markdown_report import write_markdown_report
from audio_quality_humanizer.validation.runner import run_validation
from audio_quality_humanizer.validation.status import validation_status
from audio_quality_humanizer.workflows.batch import SUPPORTED_BATCH_MODES, batch_run
from audio_quality_humanizer.workflows.doctor import doctor_file
from audio_quality_humanizer.workflows.preset_eval import preset_eval


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        report = args.handler(args)
        json_path = getattr(args, "json", None) or getattr(args, "report", None)
        if json_path:
            write_json_report(report, Path(json_path))
        if getattr(args, "markdown", None):
            write_markdown_report(report, Path(args.markdown))
        print(_status_message(report, getattr(args, "report", None)))
        if getattr(args, "fail_on_issue", False) and not report.get("passed", True):
            return 2
        if getattr(args, "fail_on_error", False) and (
            report.get("failed_files", 0) > 0 or report.get("failed_samples", 0) > 0
        ):
            return 2
        if getattr(args, "fail_on_safety", False) and not report.get("passed", True):
            return 2
        if getattr(args, "fail_on_regression", False) and not report.get("passed", True):
            return 2
        if getattr(args, "fail_if_none", False) and report.get("recommended_preset") is None:
            return 2
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-humanizer",
        description="Inspect metadata and run read-only audio quality preflights locally.",
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

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Measure read-only audio quality metrics.",
    )
    analyze_parser.add_argument("input", type=Path)
    analyze_parser.add_argument("--report", type=Path)
    analyze_parser.add_argument("--markdown", type=Path)
    analyze_parser.set_defaults(handler=_handle_analyze)

    release_check_parser = subparsers.add_parser(
        "release-check",
        help="Run a read-only technical release-readiness preflight.",
    )
    release_check_parser.add_argument("input", type=Path)
    release_check_parser.add_argument(
        "--target",
        choices=SUPPORTED_TARGETS,
        default="streaming",
    )
    release_check_parser.add_argument("--report", type=Path)
    release_check_parser.add_argument("--markdown", type=Path)
    release_check_parser.set_defaults(handler=_handle_release_check)

    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare two audio files for read-only technical regressions.",
    )
    compare_parser.add_argument("reference", type=Path)
    compare_parser.add_argument("candidate", type=Path)
    compare_parser.add_argument(
        "--target",
        choices=SUPPORTED_TARGETS,
        default="streaming",
    )
    compare_parser.add_argument("--report", type=Path)
    compare_parser.add_argument("--markdown", type=Path)
    compare_parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Return exit code 2 when blocking regressions are detected.",
    )
    compare_parser.set_defaults(handler=_handle_compare)

    humanize_parser = subparsers.add_parser(
        "humanize",
        help="Apply conservative read-guarded audio-quality processing.",
    )
    humanize_parser.add_argument("input", type=Path)
    humanize_parser.add_argument("output", type=Path)
    humanize_parser.add_argument(
        "--preset",
        choices=SUPPORTED_PRESETS,
        default="subtle",
    )
    humanize_parser.add_argument(
        "--target",
        choices=SUPPORTED_TARGETS,
        default="streaming",
    )
    humanize_parser.add_argument("--report", type=Path)
    humanize_parser.add_argument("--markdown", type=Path)
    humanize_parser.add_argument(
        "--fail-on-safety",
        action="store_true",
        help="Return exit code 2 when safety gates fail.",
    )
    humanize_parser.set_defaults(handler=_handle_humanize)

    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Run a read-only one-file metadata and release preflight.",
    )
    doctor_parser.add_argument("input", type=Path)
    doctor_parser.add_argument(
        "--target",
        choices=SUPPORTED_TARGETS,
        default="streaming",
    )
    doctor_parser.add_argument("--report", type=Path)
    doctor_parser.add_argument("--markdown", type=Path)
    doctor_parser.add_argument(
        "--fail-on-issue",
        action="store_true",
        help="Return exit code 2 when the doctor preflight does not pass.",
    )
    doctor_parser.set_defaults(handler=_handle_doctor)

    batch_parser = subparsers.add_parser(
        "batch",
        help="Run existing workflows over a folder of supported audio files.",
    )
    batch_parser.add_argument("input_dir", type=Path)
    batch_parser.add_argument(
        "--mode",
        choices=SUPPORTED_BATCH_MODES,
        default="doctor",
    )
    batch_parser.add_argument("--output-dir", type=Path)
    batch_parser.add_argument(
        "--target",
        choices=SUPPORTED_TARGETS,
        default="streaming",
    )
    batch_parser.add_argument(
        "--preset",
        choices=SUPPORTED_PRESETS,
        default="subtle",
    )
    batch_parser.add_argument("--pattern", default="*.wav")
    batch_parser.add_argument("--recursive", action="store_true")
    batch_parser.add_argument("--fail-fast", action="store_true")
    batch_parser.add_argument("--report", type=Path)
    batch_parser.add_argument("--markdown", type=Path)
    batch_parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Return exit code 2 when one or more batch files fail.",
    )
    batch_parser.set_defaults(handler=_handle_batch)

    preset_eval_parser = subparsers.add_parser(
        "preset-eval",
        help="Evaluate conservative presets on copies and recommend an eligible result.",
    )
    preset_eval_parser.add_argument("input", type=Path)
    preset_eval_parser.add_argument(
        "--target",
        choices=SUPPORTED_TARGETS,
        default="streaming",
    )
    preset_eval_parser.add_argument("--output-dir", type=Path, required=True)
    preset_eval_parser.add_argument("--presets")
    preset_eval_parser.add_argument("--report", type=Path)
    preset_eval_parser.add_argument("--markdown", type=Path)
    preset_eval_parser.add_argument(
        "--fail-if-none",
        action="store_true",
        help="Return exit code 2 when no preset is eligible.",
    )
    preset_eval_parser.set_defaults(handler=_handle_preset_eval)

    validate_parser = subparsers.add_parser(
        "validate-samples",
        help="Run local validation over user-supplied audio samples.",
    )
    validate_parser.add_argument("manifest", type=Path)
    validate_parser.add_argument("--output-dir", type=Path, required=True)
    validate_parser.add_argument(
        "--default-target",
        choices=SUPPORTED_TARGETS,
        default="streaming",
    )
    validate_parser.add_argument("--report", type=Path)
    validate_parser.add_argument("--markdown", type=Path)
    validate_parser.add_argument("--fail-fast", action="store_true")
    validate_parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Return exit code 2 when one or more validation samples fail.",
    )
    validate_parser.set_defaults(handler=_handle_validate_samples)

    validation_status_parser = subparsers.add_parser(
        "validation-status",
        help="Inspect local validation setup and report locations.",
    )
    validation_status_parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Directory to inspect. Defaults to the current working directory.",
    )
    validation_status_parser.add_argument(
        "--find",
        action="store_true",
        help="Search recursively for local validation reports.",
    )
    validation_status_parser.add_argument(
        "--max-depth",
        type=int,
        default=4,
        help="Maximum recursive search depth when --find is used.",
    )
    validation_status_parser.add_argument("--json", type=Path, help="Write JSON status report.")
    validation_status_parser.add_argument("--markdown", type=Path, help="Write Markdown status report.")
    validation_status_parser.set_defaults(handler=_handle_validation_status)

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


def _handle_analyze(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    return analyze_audio(args.input)


def _handle_release_check(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    return release_check(args.input, args.target)


def _handle_compare(args: argparse.Namespace) -> dict:
    _require_input(args.reference)
    _require_input(args.candidate)
    return compare_audio(args.reference, args.candidate, args.target)


def _handle_humanize(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    return humanize_audio(args.input, args.output, preset=args.preset, target=args.target)


def _handle_doctor(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    return doctor_file(args.input, target=args.target)


def _handle_batch(args: argparse.Namespace) -> dict:
    return batch_run(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        mode=args.mode,
        target=args.target,
        preset=args.preset,
        pattern=args.pattern,
        recursive=args.recursive,
        fail_fast=args.fail_fast,
    )


def _handle_preset_eval(args: argparse.Namespace) -> dict:
    _require_input(args.input)
    presets = _parse_presets(args.presets)
    return preset_eval(args.input, args.output_dir, target=args.target, presets=presets)


def _handle_validate_samples(args: argparse.Namespace) -> dict:
    _require_input(args.manifest)
    return run_validation(
        args.manifest,
        args.output_dir,
        default_target=args.default_target,
        fail_fast=args.fail_fast,
    )


def _handle_validation_status(args: argparse.Namespace) -> dict:
    return validation_status(args.root, find=args.find, max_depth=args.max_depth)


def _parse_presets(value: str | None) -> list[str] | None:
    if value is None:
        return None
    presets = [item.strip() for item in value.split(",") if item.strip()]
    if not presets:
        raise ValueError("--presets must include at least one preset name when provided.")
    return presets


def _require_input(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")


def _status_message(report: dict, report_path: Path | None) -> str:
    action = report.get("action", "completed")
    suffix = f"; report written to {report_path}" if report_path else ""
    if action == "preset_eval":
        eligible_count = sum(
            1
            for result in report.get("results", [])
            if result.get("humanize_passed")
            and not result.get("humanize_reverted")
            and result.get("compare_passed")
            and not result.get("blocking_issues")
        )
        return (
            f"preset eval complete; target {report.get('target')}; "
            f"recommended {report.get('recommended_preset')}; eligible {eligible_count}{suffix}"
        )
    if action == "validate_samples":
        return (
            f"validation complete; processed {report.get('processed_samples')}/"
            f"{report.get('total_samples')}; failed {report.get('failed_samples')}; "
            f"passed {report.get('passed_samples')}{suffix}"
        )
    if action == "validation_status":
        found_count = len(report.get("found_reports", []))
        if not report.get("looks_like_project_root"):
            return "validation status complete; this does not look like the project root; see suggested cd command"
        if found_count:
            return f"validation status complete; found {found_count} validation report(s)"
        if not report.get("validation_markdown_exists"):
            return "validation status complete; validation.md not found; see suggested validate-samples command"
        return "validation status complete"
    if action == "batch":
        return (
            f"batch complete; mode {report.get('mode')}; processed {report.get('processed_files')}/"
            f"{report.get('total_files')}; failed {report.get('failed_files')}{suffix}"
        )
    if action == "doctor":
        return (
            f"doctor complete; target {report.get('target')}; score {report.get('score')}; "
            f"passed {report.get('passed')}{suffix}"
        )
    if action == "humanize":
        return (
            f"humanize complete; preset {report.get('preset')}; target {report.get('target')}; "
            f"passed {report.get('passed')}; reverted {report.get('reverted')}{suffix}"
        )
    if action == "compare":
        regression_count = len(report.get("regressions", []))
        return (
            f"compare complete; target {report.get('target')}; score {report.get('score')}; "
            f"passed {report.get('passed')}; regressions {regression_count}{suffix}"
        )
    if action == "release_check":
        return (
            f"release check complete; target {report.get('target')}; "
            f"score {report.get('score')}; passed {report.get('passed')}{suffix}"
        )
    if action == "analyze":
        warning_count = len(report.get("warnings", []))
        return f"analysis complete; warnings {warning_count}{suffix}"
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
