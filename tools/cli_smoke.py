"""End-to-end CLI smoke test for local and CI use."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cli = _cli_executable()
    version_output = _run_capture([str(cli), "--version"])
    if "audio-quality-humanizer" not in version_output:
        print("CLI version output did not include package name.")
        return 1
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        sample_path = temp_dir / "sample.wav"
        humanized_path = temp_dir / "humanized.wav"
        eval_dir = temp_dir / "eval"
        validation_manifest = temp_dir / "validation_manifest.json"
        validation_dir = temp_dir / "validation_outputs"
        _write_sine(sample_path)
        _write_validation_manifest(validation_manifest, sample_path)
        original_hash = _sha256(sample_path)

        commands = [
            [
                "analyze",
                str(sample_path),
                "--report",
                str(temp_dir / "analysis.json"),
                "--markdown",
                str(temp_dir / "analysis.md"),
            ],
            [
                "release-check",
                str(sample_path),
                "--target",
                "streaming",
                "--report",
                str(temp_dir / "release.json"),
                "--markdown",
                str(temp_dir / "release.md"),
            ],
            [
                "doctor",
                str(sample_path),
                "--target",
                "streaming",
                "--report",
                str(temp_dir / "doctor.json"),
                "--markdown",
                str(temp_dir / "doctor.md"),
            ],
            [
                "humanize",
                str(sample_path),
                str(humanized_path),
                "--preset",
                "subtle",
                "--target",
                "streaming",
                "--report",
                str(temp_dir / "humanize.json"),
                "--markdown",
                str(temp_dir / "humanize.md"),
            ],
            [
                "compare",
                str(sample_path),
                str(humanized_path),
                "--target",
                "streaming",
                "--report",
                str(temp_dir / "compare.json"),
                "--markdown",
                str(temp_dir / "compare.md"),
            ],
            [
                "visualize",
                str(sample_path),
                "--report",
                str(temp_dir / "visualization.json"),
            ],
            [
                "visualize-compare",
                str(sample_path),
                str(humanized_path),
                "--target",
                "streaming",
                "--report",
                str(temp_dir / "visual_compare.json"),
            ],
            [
                "preset-eval",
                str(sample_path),
                "--target",
                "streaming",
                "--presets",
                "subtle,balanced",
                "--output-dir",
                str(eval_dir),
                "--report",
                str(temp_dir / "preset_eval.json"),
                "--markdown",
                str(temp_dir / "preset_eval.md"),
            ],
            [
                "validate-samples",
                str(validation_manifest),
                "--output-dir",
                str(validation_dir),
                "--default-target",
                "streaming",
                "--report",
                str(temp_dir / "validation.json"),
                "--markdown",
                str(temp_dir / "validation.md"),
            ],
            [
                "validation-status",
                "--root",
                str(temp_dir),
                "--find",
                "--json",
                str(temp_dir / "validation_status.json"),
                "--markdown",
                str(temp_dir / "validation_status.md"),
            ],
        ]
        for args in commands:
            _run([str(cli), *args])

        expected = [
            sample_path,
            humanized_path,
            temp_dir / "analysis.json",
            temp_dir / "analysis.md",
            temp_dir / "release.json",
            temp_dir / "release.md",
            temp_dir / "doctor.json",
            temp_dir / "doctor.md",
            temp_dir / "humanize.json",
            temp_dir / "humanize.md",
            temp_dir / "compare.json",
            temp_dir / "compare.md",
            temp_dir / "visualization.json",
            temp_dir / "visual_compare.json",
            eval_dir,
            eval_dir / "sample.subtle.humanized.wav",
            eval_dir / "sample.subtle.eval.json",
            eval_dir / "sample.balanced.humanized.wav",
            eval_dir / "sample.balanced.eval.json",
            temp_dir / "preset_eval.json",
            temp_dir / "preset_eval.md",
            validation_dir,
            validation_dir / "sample_01.validation.json",
            temp_dir / "validation.json",
            temp_dir / "validation.md",
            temp_dir / "validation_status.json",
            temp_dir / "validation_status.md",
        ]
        missing = [path for path in expected if not path.exists()]
        if missing:
            print("Missing expected smoke output files:")
            for path in missing:
                print(path)
            return 1
        if _sha256(sample_path) != original_hash:
            print("Original input file changed during CLI smoke workflow.")
            return 1

    print("CLI smoke passed.")
    return 0


def _cli_executable() -> Path:
    executable = shutil.which("ai-humanizer")
    if executable:
        return Path(executable)
    for candidate in (
        Path(sys.executable).parent / "ai-humanizer",
        Path(sys.executable).resolve().parent / "ai-humanizer",
    ):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find ai-humanizer executable.")


def _write_sine(path: Path) -> None:
    samplerate = 48000
    t = np.linspace(0.0, 1.0, samplerate, endpoint=False)
    audio = 0.2 * np.sin(2.0 * np.pi * 440.0 * t)
    sf.write(path, audio, samplerate)


def _write_validation_manifest(path: Path, sample_path: Path) -> None:
    manifest = {
        "project": "CLI smoke validation",
        "target": "streaming",
        "samples": [
            {
                "id": "sample_01",
                "path": str(sample_path),
                "target": "streaming",
                "presets": ["subtle", "balanced"],
                "notes": "Temporary smoke sample",
            }
        ],
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: list[str]) -> None:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{ROOT}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(ROOT)
    )
    subprocess.run(command, check=True, env=env)


def _run_capture(command: list[str]) -> str:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{ROOT}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(ROOT)
    )
    result = subprocess.run(command, check=True, env=env, text=True, stdout=subprocess.PIPE)
    return result.stdout


if __name__ == "__main__":
    raise SystemExit(main())
