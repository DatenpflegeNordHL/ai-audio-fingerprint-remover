"""Deterministic batch workflow runner."""

from __future__ import annotations

from pathlib import Path

from audio_quality_humanizer.analysis.metrics import analyze_audio
from audio_quality_humanizer.analysis.release_check import release_check
from audio_quality_humanizer.processing.humanize import humanize_audio
from audio_quality_humanizer.reports.json_report import write_json_report
from audio_quality_humanizer.workflows.doctor import doctor_file


SUPPORTED_BATCH_MODES = ("doctor", "analyze", "release-check", "humanize")
SUPPORTED_AUDIO_EXTENSIONS = (".wav", ".flac", ".aiff", ".aif", ".ogg")


def batch_run(
    input_dir: Path,
    output_dir: Path | None = None,
    mode: str = "doctor",
    target: str = "streaming",
    preset: str = "subtle",
    pattern: str = "*.wav",
    recursive: bool = False,
    fail_fast: bool = False,
) -> dict:
    """Run an existing workflow over supported audio files."""

    input_dir = Path(input_dir)
    output_dir = Path(output_dir) if output_dir is not None else None
    mode = mode.casefold()
    _validate_batch_args(input_dir, output_dir, mode)

    files = _discover_files(input_dir, pattern, recursive)
    warnings: list[str] = []
    if not files:
        warnings.append("No supported audio files matched the batch input.")

    results = []
    for input_path in files:
        try:
            result = _process_one(
                input_path=input_path,
                input_dir=input_dir,
                output_dir=output_dir,
                mode=mode,
                target=target,
                preset=preset,
                recursive=recursive,
            )
            results.append(result)
        except Exception as exc:
            results.append(
                {
                    "input": str(input_path),
                    "output": None,
                    "report": None,
                    "passed": False,
                    "error": str(exc),
                    "score": None,
                }
            )
            if fail_fast:
                warnings.append("Batch stopped early because fail_fast is enabled.")
                break

    failed_files = sum(1 for result in results if result["error"] is not None)
    passed_files = sum(1 for result in results if result["error"] is None and result["passed"])

    return {
        "action": "batch",
        "mode": mode,
        "target": target,
        "preset": preset,
        "input_dir": str(input_dir),
        "output_dir": str(output_dir) if output_dir is not None else None,
        "pattern": pattern,
        "recursive": recursive,
        "total_files": len(files),
        "processed_files": len(results) - failed_files,
        "failed_files": failed_files,
        "passed_files": passed_files,
        "results": results,
        "warnings": warnings,
        "notes": [
            "Batch is deterministic and does not use parallel processing in this milestone.",
            "Batch read-only modes do not alter audio files.",
            "Batch humanize writes only to output_dir and never modifies originals.",
            "Batch does not evaluate or alter watermarks, fingerprints, detector signals, provenance markers, origin markers, C2PA markers, or attribution systems.",
        ],
    }


def _validate_batch_args(input_dir: Path, output_dir: Path | None, mode: str) -> None:
    if mode not in SUPPORTED_BATCH_MODES:
        supported = ", ".join(SUPPORTED_BATCH_MODES)
        raise ValueError(f"Unsupported batch mode: {mode}. Supported modes: {supported}")
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")
    if mode == "humanize" and output_dir is None:
        raise ValueError("Batch humanize mode requires output_dir.")
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)


def _discover_files(input_dir: Path, pattern: str, recursive: bool) -> list[Path]:
    iterator = input_dir.rglob(pattern) if recursive else input_dir.glob(pattern)
    return sorted(
        path
        for path in iterator
        if path.is_file() and path.suffix.casefold() in SUPPORTED_AUDIO_EXTENSIONS
    )


def _process_one(
    *,
    input_path: Path,
    input_dir: Path,
    output_dir: Path | None,
    mode: str,
    target: str,
    preset: str,
    recursive: bool,
) -> dict:
    output_path = None
    report_path = None

    if mode == "doctor":
        report = doctor_file(input_path, target=target)
    elif mode == "analyze":
        report = analyze_audio(input_path)
    elif mode == "release-check":
        report = release_check(input_path, target=target)
    elif mode == "humanize":
        assert output_dir is not None
        output_path = _safe_output_audio_path(input_path, input_dir, output_dir, recursive)
        report = humanize_audio(input_path, output_path, preset=preset, target=target)
        report_path = output_path.with_name(f"{output_path.stem}.humanize.json")
        write_json_report(report, report_path)
    else:
        raise ValueError(f"Unsupported batch mode: {mode}")

    if mode != "humanize" and output_dir is not None:
        report_path = _safe_report_path(input_path, input_dir, output_dir, mode, recursive)
        write_json_report(report, report_path)

    return {
        "input": str(input_path),
        "output": str(output_path) if output_path is not None else None,
        "report": str(report_path) if report_path is not None else None,
        "passed": bool(report.get("passed", True)),
        "error": None,
        "score": report.get("score"),
    }


def _safe_output_audio_path(input_path: Path, input_dir: Path, output_dir: Path, recursive: bool) -> Path:
    relative = input_path.relative_to(input_dir) if recursive else Path(input_path.name)
    candidate = output_dir / relative
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return _numbered_path(candidate)


def _safe_report_path(input_path: Path, input_dir: Path, output_dir: Path, mode: str, recursive: bool) -> Path:
    relative = input_path.relative_to(input_dir) if recursive else Path(input_path.name)
    report_relative = relative.with_suffix(f".{mode}.json")
    candidate = output_dir / report_relative
    candidate.parent.mkdir(parents=True, exist_ok=True)
    return _numbered_path(candidate)


def _numbered_path(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(1, 10_000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Could not create a safe numbered filename for {path}")
